from django.http import HttpResponse
from tastypie.authentication import ApiKeyAuthentication, MultiAuthentication, SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie import fields
from tastypie.resources import ModelResource, ALL
from egg_timer.apps.periods import models as period_models
from egg_timer.apps.userprofiles import models as userprofile_models


class BaseMeta(object):
    authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
    authorization = DjangoAuthorization()


class StatisticsResource(ModelResource):
    current_cycle_length = fields.IntegerField('current_cycle_length')
    next_periods = fields.DateField('next_periods')

    class Meta(BaseMeta):
        queryset = period_models.Statistics.objects.all()
        resource_name = 'statistics'

    def get_object_list(self, request):
        return super(StatisticsResource, self).get_object_list(request).filter(
            userprofile__user=request.user)


class UserProfileResource(ModelResource):
    statistics = fields.ForeignKey(StatisticsResource, 'statistics', full=True)

    class Meta(BaseMeta):
        queryset = userprofile_models.UserProfile.objects.all()
        resource_name = 'userprofiles'

    def get_object_list(self, request):
        return super(UserProfileResource, self).get_object_list(request).filter(
            user=request.user)


class PeriodResource(ModelResource):
    userprofile = fields.ForeignKey(UserProfileResource, 'userprofile')
    start_date = fields.DateField('start_date')

    class Meta(BaseMeta):
        queryset = period_models.Period.objects.all().order_by('start_date')
        ordering = ['start_date']
        filtering = {
            'length': ALL,
            'start_date': ALL,
        }
        resource_name = 'periods'

    def create_response(self, request, data, response_class=HttpResponse,
            **response_kwargs):
        if request.GET.get('include_future'):
            statistics = period_models.Statistics.objects.filter(
                userprofile__user=request.user)[0]
            for expected_date in statistics.next_periods:
                period = {'start_date': expected_date, 'future': True}
                data['objects'].append(Bundle(data=period))
        return super(PeriodResource, self).create_response(request, data,
            response_class, **response_kwargs)

    def get_object_list(self, request):
        return super(PeriodResource, self).get_object_list(request).filter(
            userprofile__user=request.user)

    def obj_create(self, bundle, request=None, **kwargs):
        user_profile = bundle.request.user.get_profile()
        return super(PeriodResource, self).obj_create(
            bundle, request=request, userprofile=user_profile, **kwargs)
