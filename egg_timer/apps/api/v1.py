import datetime
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
    list_allowed_methods = ('get', 'post')
    detail_allowed_methods = ('get', 'post', 'put', 'delete')


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

    def get_object_list(self, request):
        return super(PeriodResource, self).get_object_list(request).filter(
            userprofile__user=request.user)

    def obj_create(self, bundle, request=None, **kwargs):
        user_profile = bundle.request.user.get_profile()
        return super(PeriodResource, self).obj_create(
            bundle, request=request, userprofile=user_profile, **kwargs)


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

        statistics = period_models.Statistics.objects.filter(
            userprofile__user=request.user)[0]
        projected_data = []
        for expected_date in statistics.next_periods:
            period = {'start_date': expected_date, 'type': 'projected period'}
            projected_data.append(Bundle(data=period))
        for expected_date in statistics.next_ovulations:
            ovulation = {'start_date': expected_date, 'type': 'projected ovulation'}
            projected_data.append(Bundle(data=ovulation))

        start_date = request.GET.get('start_date__gte')
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

        end_date = request.GET.get('start_date__lte')
        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # TODO make filtering by request user automatic, not in every query
        period_start_dates = statistics.userprofile.periods.filter(
            userprofile__user=request.user, start_date__gte=start_date, start_date__lte=end_date)
        period_start_dates = list(period_start_dates.values_list('start_date', flat=True))
        period_start_dates.extend(statistics.next_periods)

        previous_periods = statistics.userprofile.periods.filter(
            start_date__lte=start_date).order_by('-start_date')
        if previous_periods:
            previous_period = previous_periods[0]

            one_day = datetime.timedelta(days=1)
            current_date = start_date.date()
            current_day = (current_date - previous_period.start_date).days + 1
            while current_date <= datetime.date.today():
                if current_date in period_start_dates:
                    current_day = 1
                day_count = {'start_date': current_date, 'type': 'day count',
                             'text': 'Day: %s' % current_day}
                data['objects'].append(Bundle(data=day_count))
                current_date += one_day
                current_day += 1

        data['objects'].extend(projected_data)

        return super(PeriodResource, self).create_response(request, data, response_class,
                                                           **response_kwargs)
