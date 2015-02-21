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
        # data already contains period start dates; extend to contain projected data and count

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
        data['objects'].extend(projected_data)

        start_date = datetime.datetime.strptime(start_date, DATE_FORMAT)

        previous_periods = request.user.periods.filter(
            start_date__lt=start_date).order_by('-start_date')
        next_periods = request.user.periods.filter(
            start_date__gte=start_date).order_by('start_date')
        first_date = ''
        first_day = ''
        if previous_periods.exists():
            first_date = start_date.date()
            first_day = (start_date.date() - previous_periods[0].start_date).days + 1
        elif next_periods.exists():
            first_date = next_periods[0].start_date
            first_day = 1
        data['first_date'] = first_date
        data['first_day'] = first_day

        return super(PeriodDetailResource, self).create_response(request, data, response_class,
                                                                 **response_kwargs)
