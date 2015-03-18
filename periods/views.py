from collections import Counter
import datetime
from dateutil import parser as dateutil_parser
import itertools
import pytz

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

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

    def retrieve(self, request, *args, **kwargs):
        min_timestamp = request.query_params.get('min_timestamp')
        try:
            min_timestamp = datetime.datetime.strptime(min_timestamp, DATE_FORMAT)
            min_timestamp = pytz.timezone("US/Eastern").localize(min_timestamp)
        except TypeError:
            min_timestamp = period_models.today()
        instance = self.get_object()
        instance.set_start_date_and_day(min_timestamp)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@login_required
def period_form(request, period_id=None):
    try:
        timestamp = dateutil_parser.parse(request.GET.get('timestamp'))
    except (AttributeError, ValueError):
        timestamp = None
    try:
        flow_event = period_models.FlowEvent.objects.get(pk=int(period_id))
    except (TypeError, period_models.FlowEvent.DoesNotExist):
        flow_event = period_models.FlowEvent(timestamp=timestamp)
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
        'statistics_url': reverse('statistics-detail', args=[request.user.statistics.id]),
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


def _generate_cycles(start_date, end_date, cycle_length):
    current_date = start_date
    increment = datetime.timedelta(days=(cycle_length/2.0))
    values = itertools.cycle([0, 100])
    cycles = []
    while current_date < end_date:
        cycles.append([current_date, next(values)])
        current_date += increment
    day = (end_date - cycles[-1][0]).days % cycle_length
    cycles.append([end_date, round(100 * day / cycle_length)])
    return cycles


@login_required
def qigong_cycles(request):
    end_date = period_models.today() + datetime.timedelta(days=14)
    data = {}
    if request.user.birth_date:
        data = {
            'physical': _generate_cycles(request.user.birth_date, end_date, 23),
            'emotional': _generate_cycles(request.user.birth_date, end_date, 28),
            'intellectual': _generate_cycles(request.user.birth_date, end_date, 33)
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
def regenerate_key(request):
    if request.method == 'POST':
        Token.objects.filter(user=request.user).delete()
        Token.objects.create(user=request.user)

    return HttpResponseRedirect(reverse('user_profile'))
