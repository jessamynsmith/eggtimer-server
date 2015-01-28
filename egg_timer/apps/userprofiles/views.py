import datetime
import json
from urllib import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext


@login_required
def profile(request):
    # TODO add editing of profile, at least luteal phase and full name; change password would be nice
    site = site_models.Site.objects.get(id=settings.SITE_ID)
    periods_url = reverse('api_dispatch_list', kwargs={'resource_name': 'periods', 'api_name': 'v1'})
    params = {
        'username': request.user.username,
        'api_key': request.user.api_key.key
    }
    data = {
        'periods_url': '%s%s?%s' % (site.domain, periods_url, urlencode(params))
    }

    return render_to_response('userprofiles/profile.html', data, context_instance=RequestContext(request))


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
    birth_date_string = request.GET.get('birth_date')
    if birth_date_string:
        try:
            birth_date = datetime.datetime.strptime(birth_date_string, "%Y-%m-%d")
        except ValueError:
            data['error'] = "Please enter a date in the form YYYY-MM-DD, e.g. 1975-11-30"

    if request.user and request.user != auth_models.AnonymousUser():
        userprofile = request.user.get_profile()

        if userprofile.birth_date:
            birth_date = userprofile.birth_date

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

    return render_to_response('userprofiles/qigong_cycles.html', data,
                              context_instance=RequestContext(request))
