convertDataToDate = function(data) {
    for (var i=0; i<data.length; i++) {
        data[i][0] = Date.parse(data[i][0]);
    }
    return data;
};

cycle_length_frequency = function(data) {
    $('#id_cycle_length_frequency').highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: 'Cycle Length Frequency'
        },
        xAxis: {
            allowDecimals: false
        },
        yAxis: {
            title: {
                text: 'Number of Cycles'
            }
        },
        plotOptions: {
            column: {
                pointPadding: 0,
                borderWidth: 0,
                groupPadding: 0,
                shadow: false
            }
        },
        series: [{
            name: 'Number of Cycles',
            color: '#0f76ed',
            data: data.cycles
        }
        ]
    });
};

cycle_length_history = function(data) {
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
        series: [{
            name: 'Cycle length',
            color: '#0f76ed',
            data: convertDataToDate(data.cycles)
        }
        ]
    });
};

qigong_cycles = function(data) {
    $('#id_qigong_cycles').highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Qigong Cycles'
        },
        // TODO make crosshairs available anywhere on graphed line, if possible
        tooltip: {
            crosshairs: {
                color: 'black',
                dashStyle: 'longdash'
            },
            shared: true
        },
        xAxis: {
            type: 'datetime',
            range: 1 * 30 * 24 * 3600 * 1000,
            startOnTick: true,
            plotLines: [{
                color: 'black',
                dashStyle: 'longdash',
                label: {
                    rotation: 0,
                    text: 'Now'
                },
                value: Date.now(),
                width: 2
              }]
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
        series: [{
            name: 'Physical',
            color: 'red',
            data: convertDataToDate(data.physical)
        }, {
            name: 'Emotional',
            color: '#0f76ed',
            data: convertDataToDate(data.emotional)
        }, {
            name: 'Intellectual',
            color: 'purple',
            data: convertDataToDate(data.intellectual)
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
                if ($.isEmptyObject(data)) {
                    $("." + viewType + "_error").show();
                } else {
                    viewFunction(data);
                }
            }
        });
    }
};

$(document).ready(function () {
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    $('#id_select_statistics').on('change', updateView);
    updateView();
});
