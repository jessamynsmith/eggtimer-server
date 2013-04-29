from urllib import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
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
