import json
from urllib import urlencode

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from egg_timer.apps.periods import models as period_models


@login_required
def statistics(request):
    periods = period_models.Period.objects.filter(
        userprofile__user=request.user, length__isnull=False).order_by('length')
    cycle_lengths = periods.values_list('length', flat=True)
    data = {'cycle_lengths': json.dumps(list(cycle_lengths))}
    if len(cycle_lengths) > 0:
        shortest = cycle_lengths[0]
        longest = cycle_lengths[len(cycle_lengths) - 1]
        data['bins'] = range(shortest, longest + 2)  # +1 for inclusive, +1 for last bin

    url = reverse('api_dispatch_list', kwargs={'resource_name': 'periods', 'api_name': 'v1'})
    data['periods_url'] = url + '?' + urlencode({'order_by': '-start_date', 'limit': '0', 'length__isnull': False})

    return render_to_response('periods/statistics.html', data,
        context_instance=RequestContext(request))
