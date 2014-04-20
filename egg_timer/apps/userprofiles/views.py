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
    physical_cycle_length = 23
    emotional_cycle_length = 28
    intellectual_cycle_length = 33
    data = {}
    birth_date = None

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
        today = datetime.date.today()
        days_elapsed = (today - birth_date.date()).days
        physical_day = days_elapsed % physical_cycle_length
        emotional_day = days_elapsed % emotional_cycle_length
        intellectual_day = days_elapsed % intellectual_cycle_length
        data['cycles'] = {
            'physical': {
                'day': physical_day,
                'level': "%.0f" % _get_level(physical_cycle_length, days_elapsed),
                'phase': _get_phase(physical_cycle_length, physical_day),
            },
            'emotional': {
                'day': emotional_day,
                'level': "%.0f" % _get_level(emotional_cycle_length, days_elapsed),
                'phase': _get_phase(emotional_cycle_length, emotional_day),
            },
            'intellectual': {
                'day': intellectual_day,
                'level': "%.0f" % _get_level(intellectual_cycle_length, days_elapsed),
                'phase': _get_phase(intellectual_cycle_length, intellectual_day),
            }
        }

        start = today - datetime.timedelta(days=7)
        start_days = (start - birth_date.date()).days
        data['start'] = _format_date(start)
        data['today'] = _format_date(today)

        days = []
        tick_values = []
        physical = []
        emotional = []
        intellectual = []
        for i in range(0, 44):
            current_date = _format_date(start + datetime.timedelta(days=i/2.0))
            # Hack to deal with half day cycle midpoints
            if i % 2 == 1:
                current_date = "%s-0.5" % current_date
            else:
                tick_values.append(current_date)
            current_days = start_days + (i/2.0)
            days.append(current_date)
            physical.append([current_date, _get_level(physical_cycle_length, current_days)])
            emotional.append([current_date, _get_level(emotional_cycle_length, current_days)])
            intellectual.append([current_date, _get_level(intellectual_cycle_length, current_days)])
        data['days'] = json.dumps(days)
        data['tick_values'] = json.dumps(tick_values)
        data['physical'] = json.dumps(physical)
        data['emotional'] = json.dumps(emotional)
        data['intellectual'] = json.dumps(intellectual)

    return render_to_response('userprofiles/qigong_cycles.html', data,
                              context_instance=RequestContext(request))
