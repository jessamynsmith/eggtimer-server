import datetime
from dateutil import parser as dateutil_parser
import json
import pytz

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
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
            min_timestamp = period_models._today()
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
def statistics(request):
    first_days = request.user.first_days().values_list('timestamp', flat=True)
    cycle_lengths = request.user.get_cycle_lengths()
    cycles = map(list, zip([x.strftime(DATE_FORMAT) for x in first_days], cycle_lengths))
    cycle_lengths = sorted(cycle_lengths)
    data = {
        'user': request.user,
        'num_cycles': first_days.count(),
        'cycle_lengths': json.dumps(list(cycle_lengths)),
        'cycles': list(cycles)
    }
    if len(cycle_lengths) > 0:
        shortest = cycle_lengths[0]
        longest = cycle_lengths[len(cycle_lengths) - 1]
        # +1 each for inclusive, +1 for last bin
        data['bins'] = list(range(shortest, longest + 2))

    return render_to_response('periods/statistics.html', data,
                              context_instance=RequestContext(request))


@login_required
def profile(request):
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


def _get_level(cycle_length, days):
    day = days % cycle_length
    half_cycle = cycle_length / 2.0
    half_day = day
    if day > half_cycle:
        half_day = cycle_length - day

    return round(100 * half_day / half_cycle, 2)


def _get_phase(cycle_length, day):
    phase = 'waxing'
    if day > cycle_length / 2.0:
        phase = 'waning'
    return phase


def _format_date(date):
    return date.strftime("%a %b %d")


def qigong_cycles(request):
    cycles = {
        'physical': {
            'length': 23,
            'waning': 'decreasing endurance, increasing tendency to fatigue',
            'waxing': 'increasing physical strength and endurance',
        },
        'emotional': {
            'length': 28,
            'waning': 'increasing pessimism, moodiness, irritability',
            'waxing': 'increasing optimism, cheerfulness, cooperativeness',
        },
        'intellectual': {
            'length': 33,
            'waning': 'time to review old material, not learn new concepts',
            'waxing': 'time to learn new material and pursue creative and intellectual activities',
        },
    }
    data = {}
    birth_date = None

    # TODO deal with birth time and time zones
    # TODO add vertical lines at peaks
    # TODO add labels on vertical (and horizontal?) lines
    # TODO birthdate date picker
    # TODO specify date for calculation (does not have to be today)
    # TODO allow user to select their current timezone
    birth_date_string = request.POST.get('birth_date')
    if birth_date_string:
        try:
            birth_date = datetime.datetime.strptime(birth_date_string, DATE_FORMAT)
            request.user.birth_date = pytz.timezone("US/Eastern").localize(birth_date)
            request.user.save()
        except ValueError:
            data['error'] = "Please enter a date in the form YYYY-MM-DD, e.g. 1975-11-30"

    if request.user and not request.user.is_anonymous():
        if request.user.birth_date:
            birth_date = request.user.birth_date

    if birth_date:
        data['birth_date'] = str(birth_date.date())
        data['cycles'] = {}
        today = datetime.date.today()
        days_elapsed = (today - birth_date.date()).days
        for cycle_type in cycles:
            cycle_length = cycles[cycle_type]['length']
            current_day = days_elapsed % cycle_length
            description = cycles[cycle_type][_get_phase(cycle_length, current_day)]
            data['cycles'][cycle_type] = {
                'length': cycle_length,
                'day': current_day,
                'level': "%.0f" % _get_level(cycle_length, days_elapsed),
                'phase': description,
                'data': []
            }

        start = today - datetime.timedelta(days=7)
        start_days = (start - birth_date.date()).days
        data['start'] = _format_date(start)
        data['today'] = _format_date(today)
        data['today_with_year'] = str(today)

        tick_values = []
        for i in range(0, 43):
            current_date = _format_date(start + datetime.timedelta(days=i/2.0))
            # Hack to deal with half day cycle midpoints
            if i % 2 == 1:
                current_date = "%s-0.5" % current_date
            else:
                tick_values.append(current_date)
            current_days = start_days + (i/2.0)
            for cycle_type in cycles:
                cycle_length = cycles[cycle_type]['length']
                level = _get_level(cycle_length, current_days)
                data['cycles'][cycle_type]['data'].append([current_date, level])
        data['tick_values'] = json.dumps(tick_values)
        for cycle_type in cycles:
            data['cycles'][cycle_type]['data'] = json.dumps(data['cycles'][cycle_type]['data'])

    return render_to_response('periods/qigong_cycles.html', data,
                              context_instance=RequestContext(request))
