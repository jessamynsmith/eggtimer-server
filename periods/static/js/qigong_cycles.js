qigong_cycles_old = function(tickValues, physicalData, emotionalData, intellectualData,
physicalLevel, emotionalLevel, intellectualLevel, startDate, todayDate) {
    // TODO change to highcharts

    var width = $(window).width() - 110;
    var height = 300;
    var padding = {top: 15, right: 15, bottom: 70, left: 60};

    var xScale = d3.scale.ordinal()
            .domain(physicalData.map(function (d) {
                return d[0];
            }))
            .rangePoints([0, width]);

    var yScale = d3.scale.linear()
            .range([height, 0])
            .domain([0, 100]);

    var xAxis = d3.svg.axis()
            .scale(xScale)
            .orient("bottom")
            .tickValues(tickValues);

    var yAxis = d3.svg.axis()
            .scale(yScale)
            .orient("left");

    var line = d3.svg.line()
            .x(function (d) {
                return xScale(d[0]);
            })
            .y(function (d) {
                return yScale(d[1]);
            });

    var svg = d3.select("body").append("svg")
            .attr("width", width + padding.left + padding.right)
            .attr("height", height + padding.top + padding.bottom)
            .append("g")
            .attr("transform", "translate(" + padding.left + "," + padding.top + ")");

    svg.append("path")
            .datum(physicalData)
            .attr("class", "physical")
            .attr("d", line);

    svg.append("path")
            .datum(emotionalData)
            .attr("class", "emotional")
            .attr("d", line);

    svg.append("path")
            .datum(intellectualData)
            .attr("class", "intellectual")
            .attr("d", line);

    svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-1em")
            .attr("dy", "0.6em")
            .attr("transform", function (d) {
                return "rotate(-35)";
            });

    svg.append("g")
            .attr("class", "y axis")
            .call(yAxis);

    var today = svg.selectAll('path.median.x')
            .data([
                [
                    [todayDate, 0],
                    [todayDate, 100]
                ]
            ])
            .enter()
            .append('svg:path')
            .attr('class', 'line')
            .style("stroke-dasharray", ("3, 3"))
            .attr("d", d3.svg.line()
                    .x(function (d, i) {
                        return xScale(d[0]);
                    })
                    .y(function (d, i) {
                        return yScale(d[1]);
                    })
            );

    var physical = svg.selectAll('path.median.y')
            .data([
                [
                    [startDate, physicalLevel],
                    [todayDate, physicalLevel]
                ]
            ])
            .enter()
            .append('svg:path')
            .attr('class', 'physical')
            .style("stroke-dasharray", ("3, 3"))
            .attr("d", d3.svg.line()
                    .x(function (d, i) {
                        return xScale(d[0]);
                    })
                    .y(function (d, i) {
                        return yScale(d[1]);
                    })
            );

    var emotional = svg.selectAll('path.median.y')
            .data([
                [
                    [startDate, emotionalLevel],
                    [todayDate, emotionalLevel]
                ]
            ])
            .enter()
            .append('svg:path')
            .attr('class', 'emotional')
            .style("stroke-dasharray", ("3, 3"))
            .attr("d", d3.svg.line()
                    .x(function (d, i) {
                        return xScale(d[0]);
                    })
                    .y(function (d, i) {
                        return yScale(d[1]);
                    })
            );

    var intellectual = svg.selectAll('path.median.y')
            .data([
                [
                    [startDate, intellectualLevel],
                    [todayDate, intellectualLevel]
                ]
            ])
            .enter()
            .append('svg:path')
            .attr('class', 'intellectual')
            .style("stroke-dasharray", ("3, 3"))
            .attr("d", d3.svg.line()
                    .x(function (d, i) {
                        return xScale(d[0]);
                    })
                    .y(function (d, i) {
                        return yScale(d[1]);
                    })
            );

};

qigong_cycles = function() {
    $('#id_cycle_length_history').highcharts({
        chart: {
            type: 'line'
        },
        title: {
            text: 'Qigong Cycles'
        },
        xAxis: {
            categories: JSON.parse($('#id_cycle_starts').text())
        },
        yAxis: {
            title: {
                text: 'Cycle Length'
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
            name: 'Cycle length',
            data: JSON.parse($('#id_cycle_lengths').text())
        }
        ]
    });
};

$(document).ready(function () {
    qigong_cycles();
});
