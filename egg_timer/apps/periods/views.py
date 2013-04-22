from itertools import izip
import json
import math

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext

from matplotlib import pyplot
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

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
        data['bins'] = range(shortest, longest + 2) # +1 for inclusive, +1 for last bin

    return render_to_response('periods/statistics.html', data,
        context_instance=RequestContext(request))


def grouped(iterable, n):
    """s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."""
    return izip(*[iter(iterable)]*n)


@login_required
def frequencies(request):
    periods = period_models.Period.objects.filter(
        userprofile__user=request.user, length__isnull=False).order_by('length')
    if len(periods) < 1:
        raise Http404

    cycle_lengths = periods.values_list('length', flat=True)
    shortest = cycle_lengths[0]
    longest = cycle_lengths[len(cycle_lengths) - 1]

    fig = pyplot.figure()
    ax = fig.add_subplot(111)

    # the histogram of the data
    bins = [x - 0.5 for x in range(shortest, longest + 2)]
    n, bins, patches = ax.hist(cycle_lengths, bins=bins)
    y_range = n.max(0) + 1
    pyplot.xticks(range(shortest, longest + 1))

    y_step = int(math.ceil(y_range / 10.0))
    y_ticks = [x[0] for x in grouped(range(y_range), y_step)]
    y_ticks.append(y_ticks[-1] + y_step)
    pyplot.yticks(y_ticks)

    ax.set_xlabel('Cycle Length')
    ax.set_ylabel('Count')
    ax.set_title('Cycle Length Frequency')
    ax.set_xlim(shortest - 1.5, longest + 1.5)
    ax.set_ylim(0, y_range)
    ax.yaxis.grid(True)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
