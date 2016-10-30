from collections import Counter
import datetime
import itertools
import math
import pytz

from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.dateparse import parse_datetime
from django.views.generic import CreateView, TemplateView, UpdateView

from extra_views import ModelFormSetView
from jsonview.views import JsonView
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

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


class ApiAuthenticateView(APIView):
    http_method_names = ['post']
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user = None
        error = ''
        status_code = status.HTTP_400_BAD_REQUEST

        try:
            email = request.data['email']
            password = request.data['password']
            user = auth.authenticate(username=email, password=password)
            if not user:
                status_code = status.HTTP_401_UNAUTHORIZED
                error = "Invalid credentials"
        except KeyError as e:
            error = "Missing required field '%s'" % e.args[0]

        if user:
            return Response({'token': user.auth_token.key})

        return Response({'error': error}, status=status_code)


class AerisView(LoginRequiredMixin, JsonView):
    def get_context_data(self, **kwargs):
        context = super(AerisView, self).get_context_data(**kwargs)
        from_date = self.request.GET.get('min_timestamp')
        to_date = self.request.GET.get('max_timestamp')
        data = period_models.AerisData.get_for_date(from_date, to_date)
        if data:
            context.update(data)
        return context


class FlowEventMixin(LoginRequiredMixin):
    model = period_models.FlowEvent
    form_class = period_forms.PeriodForm

    def set_to_utc(self, timestamp):
        user_timezone = pytz.timezone(self.request.user.timezone.zone)
        localized = timestamp
        if localized.tzinfo:
            localized = localized.astimezone(user_timezone)
        localized_in_utc = localized.replace(tzinfo=pytz.utc)
        return localized_in_utc

    def get_timestamp(self):
        # e.g. ?timestamp=2015-08-19T08:31:24-07:00
        timestamp = self.request.GET.get('timestamp')
        try:
            timestamp = parse_datetime(timestamp)
        except TypeError as e:
            print("Could not parse date: %s" % e)
        if not timestamp:
            timestamp = period_models.today()
        timestamp = self.set_to_utc(timestamp)
        return timestamp


class FlowEventCreateView(FlowEventMixin, CreateView):
    def is_first_day(self, timestamp):
        yesterday = timestamp - datetime.timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0)
        yesterday_events = period_models.FlowEvent.objects.filter(
            timestamp__gte=yesterday_start, timestamp__lte=timestamp)
        if yesterday_events.count():
            return False
        return True

    def get_initial(self):
        timestamp = self.get_timestamp()
        initial = {
            'timestamp': timestamp,
            'first_day': self.is_first_day(timestamp)
        }
        return initial


class FlowEventUpdateView(FlowEventMixin, UpdateView):
    def get_object(self, queryset=None):
        obj = super(FlowEventUpdateView, self).get_object(queryset)
        obj.timestamp = self.set_to_utc(obj.timestamp)
        return obj


class FlowEventFormSetView(LoginRequiredMixin, ModelFormSetView):
    model = period_models.FlowEvent
    exclude = ['user']
    extra = 10

    def get_queryset(self):
        queryset = self.model.objects.filter(user=self.request.user).order_by('timestamp')
        return queryset


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'periods/calendar.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        context['periods_url'] = self.request.build_absolute_uri(reverse('periods-list'))
        context['statistics_url'] = self.request.build_absolute_uri(reverse('statistics-list'))
        context['flow_event_url'] = self.request.build_absolute_uri(reverse('flow_event_create'))
        context['aeris_url'] = self.request.build_absolute_uri(reverse('aeris'))
        return context


class CycleLengthFrequencyView(LoginRequiredMixin, JsonView):
    def get_context_data(self, **kwargs):
        context = super(CycleLengthFrequencyView, self).get_context_data(**kwargs)
        cycle_lengths = self.request.user.get_cycle_lengths()
        cycles = []
        if cycle_lengths:
            cycle_counter = Counter(cycle_lengths)
            cycles = list(zip(cycle_counter.keys(), cycle_counter.values()))
        context['cycles'] = cycles
        return context


class CycleLengthHistoryView(LoginRequiredMixin, JsonView):
    def get_context_data(self, **kwargs):
        context = super(CycleLengthHistoryView, self).get_context_data(**kwargs)
        cycle_lengths = self.request.user.get_cycle_lengths()
        cycles = []
        if cycle_lengths:
            first_days = list(self.request.user.first_days().values_list('timestamp', flat=True))
            cycles = list(zip([x.strftime(DATE_FORMAT) for x in first_days], cycle_lengths))
        context['cycles'] = cycles
        return context


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


class QigongCycleView(LoginRequiredMixin, JsonView):
    def get_context_data(self, **kwargs):
        context = super(QigongCycleView, self).get_context_data(**kwargs)
        today = period_models.today()
        end_date = period_models.today() + datetime.timedelta(days=14)
        user = self.request.user
        if user.birth_date:
            context['physical'] = _generate_cycles(user.birth_date, today, end_date, 23)
            context['emotional'] = _generate_cycles(user.birth_date, today, end_date, 28)
            context['intellectual'] = _generate_cycles(user.birth_date, today, end_date, 33)
        return context


class StatisticsView(TemplateView):
    template_name = 'periods/statistics.html'

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)
        first_days = list(self.request.user.first_days().values_list('timestamp', flat=True))
        graph_types = [
            ['cycle_length_frequency', 'Cycle Length Frequency'],
            ['cycle_length_history', 'Cycle Length History'],
            ['qigong_cycles', 'Qigong Cycles']
        ]
        # TODO days of bleeding, what else?
        context['first_days'] = first_days
        context['graph_types'] = graph_types
        return context


# TODO give user option to delete account
# TODO allow user to change email address?
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['first_name', 'last_name', 'send_emails', '_timezone', 'birth_date',
              'luteal_phase_length']

    def get_object(self, *args, **kwargs):
        return self.request.user

    def get_success_url(self):
        return reverse('user_profile')


class ApiInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'periods/api_info.html'

    def get_context_data(self, **kwargs):
        context = super(ApiInfoView, self).get_context_data(**kwargs)
        context['periods_url'] = self.request.build_absolute_uri(reverse('periods-list'))
        return context


class RegenerateKeyView(LoginRequiredMixin, UpdateView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        Token.objects.create(user=request.user)

        return HttpResponseRedirect(reverse('api_info'))
