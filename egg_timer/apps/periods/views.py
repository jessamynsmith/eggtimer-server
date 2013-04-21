from itertools import izip
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
    return render_to_response('periods/statistics.html', {},
        context_instance=RequestContext(request))


def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return izip(*[iter(iterable)]*n)


@login_required
def frequencies(request):
    periods = period_models.Period.objects.filter(userprofile__user=request.user)
    cycle_lengths = [x for x in periods.values_list('length', flat=True) if x is not None]
    if not cycle_lengths:
        raise Http404
    distinct = set(cycle_lengths)
    in_order = sorted(cycle_lengths)

    fig = pyplot.figure()
    ax = fig.add_subplot(111)

    # the histogram of the data
    bins = [x - 0.5 for x in distinct]
    bins.append(bins[-1] + 1)
    n, bins, patches = ax.hist(in_order, bins=bins)
    y_range = n.max(0) + 1
    pyplot.xticks(range(in_order[0], in_order[-1] + 1))

    y_step = int(math.ceil(y_range / 10.0))
    y_ticks = [x[0] for x in grouped(range(y_range), y_step)]
    y_ticks.append(y_ticks[-1] + y_step)
    pyplot.yticks(y_ticks)

    ax.set_xlabel('Cycle Length')
    ax.set_ylabel('Count')
    ax.set_title('Cycle Length Frequency')
    ax.set_xlim(in_order[0] - 1.5, in_order[-1] + 1.5)
    ax.set_ylim(0, y_range)
    ax.yaxis.grid(True)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response