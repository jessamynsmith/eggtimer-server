import datetime

from django.http import HttpResponse
import pytz
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

    class Meta(BaseMeta):
        queryset = period_models.FlowEvent.objects.all().order_by('timestamp')
        ordering = ['timestamp']
        filtering = {
            'length': ALL,
            'timestamp': ALL,
            'first_day': ALL,
            'level': ALL,
            'color': ALL,
            'clots': ALL,
            'comment': ALL,
        }
        resource_name = 'periods'

    def obj_create(self, bundle, request=None, **kwargs):
        return super(PeriodResource, self).obj_create(
            bundle, request=request, user=bundle.request.user, **kwargs)


class PeriodDetailResource(PeriodResource):

    class Meta(PeriodResource.Meta):
        resource_name = 'periods_detail'

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        # data already contains period start dates; extend to contain projected data and count

        start_timestamp = request.GET.get('timestamp__gte')
        end_timestamp = request.GET.get('timestamp__lte')
        if not start_timestamp or not end_timestamp:
            raise BadRequest("Must specify date range, e.g. timestamp__gte=<date>&"
                             "timestamp__lte=<date>")

        projected_data = []
        for expected_date in request.user.statistics.next_periods:
            period = {'timestamp': expected_date, 'type': 'projected period'}
            projected_data.append(Bundle(data=period))
        for expected_date in request.user.statistics.next_ovulations:
            ovulation = {'timestamp': expected_date, 'type': 'projected ovulation'}
            projected_data.append(Bundle(data=ovulation))
        data['objects'].extend(projected_data)

        # TODO How to handle timezones? Have it specified in request?
        start_timestamp = datetime.datetime.strptime(start_timestamp, DATE_FORMAT)
        start_timestamp = pytz.timezone("US/Eastern").localize(start_timestamp)

        previous_period = request.user.get_previous_period(start_timestamp)
        next_period = request.user.get_next_period(start_timestamp)
        first_date = ''
        first_day = ''
        if previous_period:
            first_date = start_timestamp.date()
            first_day = (start_timestamp - previous_period.timestamp).days + 1
        elif next_period:
            first_date = next_period.timestamp.date()
            first_day = 1
        data['first_date'] = first_date
        data['first_day'] = first_day

        return super(PeriodDetailResource, self).create_response(request, data, response_class,
                                                                 **response_kwargs)
