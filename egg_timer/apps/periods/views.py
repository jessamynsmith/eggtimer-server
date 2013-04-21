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
    n, bins, patches = ax.hist(in_order, bins=len(distinct))
    y_range = n.max(0) + 1
    pyplot.xticks(range(in_order[0], in_order[-1]))
    pyplot.yticks([y for y in range(y_range)])

    ax.set_xlabel('Cycle Length')
    ax.set_ylabel('Count')
    ax.set_title('Cycle Length Frequency')
    ax.set_xlim(in_order[0]-1.5, in_order[-1]+1.5)
    ax.set_ylim(0, y_range)

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response