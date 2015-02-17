import datetime

from django.http import HttpResponse
from tastypie.authentication import ApiKeyAuthentication, MultiAuthentication, SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest
from tastypie import fields
from tastypie.resources import ModelResource, ALL

from periods import models as period_models


DATE_FORMAT = "%Y-%m-%d"


class EggTimerResource(ModelResource):

    def get_object_list(self, request):
        return super(EggTimerResource, self).get_object_list(request).filter(user=request.user)


class BaseMeta(object):
    authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
    authorization = DjangoAuthorization()
    list_allowed_methods = ('get', 'post')
    detail_allowed_methods = ('get', 'post', 'put', 'delete')


class StatisticsResource(EggTimerResource):
    current_cycle_length = fields.IntegerField('current_cycle_length')
    next_periods = fields.DateField('next_periods')

    class Meta(BaseMeta):
        queryset = period_models.Statistics.objects.all()
        resource_name = 'statistics'


class UserResource(EggTimerResource):
    statistics = fields.ForeignKey(StatisticsResource, 'statistics', full=True)

    class Meta(BaseMeta):
        queryset = period_models.User.objects.all()
        resource_name = 'users'


class PeriodResource(EggTimerResource):
    user = fields.ForeignKey(UserResource, 'user')
    start_date = fields.DateField('start_date')

    class Meta(BaseMeta):
        queryset = period_models.Period.objects.all().order_by('start_date')
        ordering = ['start_date']
        filtering = {
            'length': ALL,
            'start_date': ALL,
        }
        resource_name = 'periods'

    def obj_create(self, bundle, request=None, **kwargs):
        return super(PeriodResource, self).obj_create(
            bundle, request=request, user=bundle.request.user, **kwargs)


class PeriodDetailResource(PeriodResource):

    class Meta(BaseMeta):
        queryset = period_models.Period.objects.all().order_by('start_date')
        ordering = ['start_date']
        filtering = {
            'length': ALL,
            'start_date': ALL,
        }
        resource_name = 'periods_detail'

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        # data already contains period start dates; extend to contain projected data and day counts

        start_date = request.GET.get('start_date__gte')
        end_date = request.GET.get('start_date__lte')
        if not start_date or not end_date:
            raise BadRequest("Must specify date range, e.g. start_date__gte=<date>&"
                             "start_date__lte=<date>")

        projected_data = []
        for expected_date in request.user.statistics.next_periods:
            period = {'start_date': expected_date, 'type': 'projected period'}
            projected_data.append(Bundle(data=period))
        for expected_date in request.user.statistics.next_ovulations:
            ovulation = {'start_date': expected_date, 'type': 'projected ovulation'}
            projected_data.append(Bundle(data=ovulation))

        start_date = datetime.datetime.strptime(start_date, DATE_FORMAT)
        end_date = datetime.datetime.strptime(end_date, DATE_FORMAT)

        period_start_dates = request.user.periods.filter(
            start_date__gte=start_date, start_date__lte=end_date).order_by('start_date')
        period_start_dates = list(period_start_dates.values_list('start_date', flat=True))
        period_start_dates.extend(request.user.statistics.next_periods)

        one_day = datetime.timedelta(days=1)

        previous_periods = request.user.periods.filter(
            start_date__lt=start_date).order_by('-start_date')
        if previous_periods.exists():
            current_date = start_date.date()
            current_day = (start_date.date() - previous_periods[0].start_date).days + 1
        elif len(period_start_dates):
            current_date = period_start_dates[0]
            current_day = 1
        else:
            # Bump date past end date so we don't create any day counts
            current_date = end_date.date() + one_day
            current_day = None

        while current_date <= end_date.date():
            if current_date in period_start_dates:
                current_day = 1
            day_count = {'start_date': current_date, 'type': 'day count',
                         'text': 'Day: %s' % current_day}
            projected_data.append(Bundle(data=day_count))
            current_date += one_day
            current_day += 1

        data['objects'].extend(projected_data)

        return super(PeriodDetailResource, self).create_response(request, data, response_class,
                                                                 **response_kwargs)
