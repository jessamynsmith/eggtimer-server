from collections import Counter
import datetime
from dateutil import parser as dateutil_parser
import itertools
import json
import math
import pytz

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from periods import forms as period_forms, models as period_models, serializers


DATE_FORMAT = "%Y-%m-%d"


class FlowEventViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FlowEventSerializer
    filter_class = serializers.FlowEventFilter

    def get_queryset(self):
        return period_models.FlowEvent.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StatisticsViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.StatisticsSerializer

    def get_queryset(self):
        return period_models.Statistics.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Only return a single statistics object, for the authenticated user
        min_timestamp = request.query_params.get('min_timestamp')
        try:
            min_timestamp = datetime.datetime.strptime(min_timestamp, DATE_FORMAT)
            min_timestamp = pytz.timezone(request.user.timezone.zone).localize(min_timestamp)
        except TypeError:
            min_timestamp = period_models.today()
        queryset = self.filter_queryset(self.get_queryset())
        instance = queryset[0]
        instance.set_start_date_and_day(min_timestamp)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_authenticate(request):
    user = None
    data = None
    status_code = 400
    error = None

    try:
        data = json.loads(request.body.decode())
    except ValueError:
        error = "Could not parse body as JSON"

    if not error:
        try:
            email = data['email']
            password = data['password']
            user = auth.authenticate(username=email, password=password)
            if not user:
                status_code = 401
                error = "Invalid credentials"
        except KeyError as e:
            error = "Missing required field '%s'" % e.args[0]

    if user:
        return JsonResponse({'token': user.auth_token.key})

    return JsonResponse({'error': error}, status=status_code)


@login_required
def period_form(request, period_id=None):
    # e.g. /period_form/?timestamp=2015-08-19T08:31:24-07:00
    user_timezone = pytz.timezone(request.user.timezone.zone)
    try:
        flow_event = period_models.FlowEvent.objects.get(pk=int(period_id))
        flow_event.timestamp = flow_event.timestamp.astimezone(user_timezone)
    except (TypeError, period_models.FlowEvent.DoesNotExist):
        timestamp = request.GET.get('timestamp')
        try:
            timestamp = dateutil_parser.parse(timestamp)
        except AttributeError:
            timestamp = period_models.today().astimezone(user_timezone)
        flow_event = period_models.FlowEvent(timestamp=timestamp)
        if timestamp:
            yesterday = timestamp - datetime.timedelta(days=1)
            yesterday_start = yesterday.replace(hour=0, minute=0, second=0)
            yesterday_events = period_models.FlowEvent.objects.filter(
                timestamp__gte=yesterday_start, timestamp__lte=timestamp)
            if not yesterday_events.count():
                flow_event.first_day = True
    flow_event.timestamp = flow_event.timestamp.replace(tzinfo=pytz.utc)
    form = period_forms.PeriodForm(instance=flow_event)
    data = {
        'form': form,
    }
    return render_to_response('periods/period_form.html', data,
                              context_instance=RequestContext(request))


@login_required
def calendar(request):
    data = {
        'periods_url': reverse('periods-list'),
        'statistics_url': reverse('statistics-list'),
        'period_form_url': reverse('period_form'),
    }

    return render_to_response('periods/calendar.html', data,
                              context_instance=RequestContext(request))


@login_required
def cycle_length_frequency(request):
    cycle_lengths = request.user.get_cycle_lengths()
    data = {}
    if cycle_lengths:
        cycle_counter = Counter(cycle_lengths)
        data = {
            'cycles': list(zip(cycle_counter.keys(), cycle_counter.values()))
        }
    return JsonResponse(data)


@login_required
def cycle_length_history(request):
    cycle_lengths = request.user.get_cycle_lengths()
    data = {}
    if cycle_lengths:
        first_days = list(request.user.first_days().values_list('timestamp', flat=True))
        data = {
            'cycles': list(zip([x.strftime(DATE_FORMAT) for x in first_days], cycle_lengths))
        }
    return JsonResponse(data)


def _get_level(start_date, today, cycle_length):
    cycle_length_seconds = datetime.timedelta(days=cycle_length).total_seconds()
    current_phase = (today - start_date).total_seconds() / cycle_length_seconds
    # Standard sine starts at 0, with maximum of 1, minimum of -1, and period of 2pi
    # Our graph starts at 0, with maximum of 100, minimum of 0, and period of cycle_length
    # -0.5 radians shifts the graph 1/4 period to the right
    # +1 shifts the graph up 1 unit
    # *50 takes the max from 2 to 100
    return round(50 * (math.sin(math.pi * (2 * current_phase - 0.5)) + 1))


def _generate_cycles(start_date, today, end_date, cycle_length):
    current_date = start_date
    increment = datetime.timedelta(days=(cycle_length / 2.0))
    values = itertools.cycle([0, 100])
    cycles = []
    while current_date < today:
        cycles.append([current_date, next(values)])
        current_date += increment
    cycles.append([today, _get_level(start_date, today, cycle_length)])
    while current_date < end_date:
        cycles.append([current_date, next(values)])
        current_date += increment
    cycles.append([end_date, _get_level(start_date, end_date, cycle_length)])
    return cycles


@login_required
def qigong_cycles(request):
    today = period_models.today()
    end_date = period_models.today() + datetime.timedelta(days=14)
    data = {}
    if request.user.birth_date:
        data = {
            'physical': _generate_cycles(request.user.birth_date, today, end_date, 23),
            'emotional': _generate_cycles(request.user.birth_date, today, end_date, 28),
            'intellectual': _generate_cycles(request.user.birth_date, today, end_date, 33)
        }
    return JsonResponse(data)


@login_required
def statistics(request):
    first_days = list(request.user.first_days().values_list('timestamp', flat=True))
    graph_types = [
        ['cycle_length_frequency', 'Cycle Length Frequency'],
        ['cycle_length_history', 'Cycle Length History'],
        ['qigong_cycles', 'Qigong Cycles']
    ]
    data = {
        'user': request.user,
        'first_days': first_days,
        # TODO days of bleeding, what else?
        'graph_types': graph_types
    }
    return render_to_response('periods/statistics.html', data,
                              context_instance=RequestContext(request))


@login_required
def profile(request):
    # TODO give user option to delete account
    # TODO allow user to change email address?
    if request.method == 'POST':
        form = period_forms.UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = period_forms.UserForm(instance=request.user)

    data = {
        'form': form,
        'periods_url': request.build_absolute_uri(reverse('periods-list'))
    }

    return render_to_response('periods/profile.html', data,
                              context_instance=RequestContext(request))


@login_required
def api_info(request):
    data = {
        'periods_url': request.build_absolute_uri(reverse('periods-list'))
    }
    return render_to_response('periods/api_info.html', data,
                              context_instance=RequestContext(request))


@login_required
def regenerate_key(request):
    if request.method == 'POST':
        Token.objects.filter(user=request.user).delete()
        Token.objects.create(user=request.user)

    return HttpResponseRedirect(reverse('api_info'))
