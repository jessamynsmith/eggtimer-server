var rendered = {
    'cycle_length_frequency': false,
    'cycle_length_history': false
};

cycle_length_frequency = function(data) {
    $('#id_cycle_length_frequency').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: 'Cycle Length Frequency'
        },
        yAxis: {
            title: {
                text: 'Number of Cycles'
            }
        },
        plotOptions: {
            column: {
                color: '#0f76ed',
                pointPadding: 0,
                borderWidth: 0,
                groupPadding: 0,
                shadow: false
            }
        },
        series: [{
            name: 'Number of Cycles',
            data: data
        }
        ]
    });
    rendered.cycle_length_frequency = true;
};

cycle_length_history = function(data) {
    for (var i=0; i<data.length; i++) {
        data[i][0] = Date.parse(data[i][0]);
    }
    $('#id_cycle_length_history').highcharts({
        chart: {
            type: 'line',
            zoomType: 'x'
        },
        title: {
            text: 'Cycle Length History'
        },
        xAxis: {
            type: 'datetime',
            range: 6 * 30 * 24 * 3600 * 1000
        },
        rangeSelector: {
            enabled: true
        },
        scrollbar: {
            enabled: true
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Cycle Length'
            }
        },
        plotOptions: {
            line: {
                color: '#0f76ed'
            }
        },
        series: [{
            name: 'Cycle length',
            data: data
        }
        ]
    });
};

updateView = function() {
    $('.statistics').hide();
    var viewType = $('#id_select_statistics').val();
    $("#id_" + viewType).show();

    var viewFunction = window[viewType];
    if (typeof viewFunction === "function") {
        $.ajax({
            url: viewType,
            contentType: 'application/json',
            success: function (data, textStatus, jqXHR) {
                viewFunction(data);
            }
        });
    }
};

$(document).ready(function () {
    $('#id_select_statistics').on('change', updateView);
    updateView();
});
