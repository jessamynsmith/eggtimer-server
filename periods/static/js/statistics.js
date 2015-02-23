
cycle_length_frequency = function(bins, cycle_lengths) {
    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var width = $(window).width() - 20;
    var height = Math.round($(window).height() * 0.80);
    var padding = {top: 30, right: 15, bottom: 50, left: 30};

    var data = d3.layout.histogram()
            .bins(bins)
            (cycle_lengths);

    var xScale = d3.scale.ordinal()
            .domain(data.map(function (d) {
                return d.x;
            }))
            .rangeRoundBands([0, width - padding.left - padding.right], 0.1);

    var ymax = d3.max(data, function (d) {
        return d.y;
    });
    var yScale = d3.scale.linear()
            .domain([0, ymax])
            .rangeRound([height - padding.bottom, padding.top]);

    var svg = d3.select("body")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

    var bar = svg.selectAll(".bar")
            .data(data)
            .enter().append("g")
            .attr("class", "bar")
            .attr("transform", function (d) {
                return "translate(" + xScale(d.x) + ", " + yScale(d.y) + ")";
            });

    bar.append("rect")
            .attr("data-placement", "top")
            .attr("width", xScale.rangeBand())
            .attr("height", function (d) {
                return height - yScale(d.y) - padding.bottom;
            });

    bar.append("text")
            .attr("dy", ".75em")
            .attr("y", 6)
            .attr("x", function (d) {
                return xScale.rangeBand() * (d.dx - data[0].dx + 0.5);
            })
            .attr("text-anchor", "middle")
            .text(function (d) {
                return formatCount(d.y);
            });

    // Axis
    var xAxis = d3.svg.axis()
            .scale(xScale)
            .orient("bottom")
            .tickSize(6, 0);

    svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + (height - padding.bottom) + ")")
            .call(xAxis);

    svg.append("text")
            .attr("class", "x label")
            .attr("text-anchor", "middle")
            .attr("x", width / 2)
            .attr("y", height - 4)
            .text("Cycle Length (days)");

    svg.append("text")
            .attr("class", "y label")
            .attr("text-anchor", "center")
            .attr("x", -height / 2)
            .attr("y", 18)
            .attr("transform", "rotate(-90)")
            .text("Number of Cycles");

    // Title
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 15)
        .attr("text-anchor", "middle")
        .attr("class", "h4")
        .text("Cycle Length Frequency");
};


cycle_length_history = function(data) {
    var width = $(window).width() - 20;
    var height = Math.round($(window).height() * 0.80);
    var padding = {top: 50, right: 10, bottom: 75, left: 65};

    var xScale = d3.scale.ordinal()
            .domain(data.map(function (d) {
                return d[0];
            }))
            .rangeRoundBands([padding.left, width - padding.left - padding.right], 0.1);

    var yScale = d3.scale.linear()
            .domain([0, d3.max(data, function (d) {
                return d[1];
            })])
            .range([height - padding.bottom, padding.top]);


    var svg = d3.select("body")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

    var bar = svg.selectAll(".bar")
            .data(data)
            .enter().append("g")
            .attr("class", "bar")
            .attr("transform", function (d) {
                return "translate(" + xScale(d[0]) + ", " + yScale(d[1]) + ")";
            });

    bar.append("rect")
            .attr("data-placement", "top")
            .attr("width", xScale.rangeBand())
            .attr("height", function (d) {
                return height - yScale(d[1]) - padding.bottom;
            });

    var step = Math.round(data.length / 12);
    var tickValues = [];
    var i = 0;
    data.forEach(function (d) {
        if (i % step === 0) {
            tickValues.push(d[0]);
        }
        i++;
    });
    var xAxis = d3.svg.axis()
            .scale(xScale)
            .orient("bottom")
            .tickSize(6, 0)
            .tickValues(tickValues);

    svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + (height - padding.bottom) + ")")
            .call(xAxis)
            .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-1em")
            .attr("dy", "0.6em")
            .attr("transform", function (d) {
                return "rotate(-35)";
            });

    svg.append("text")
            .attr("class", "x label")
            .attr("text-anchor", "middle")
            .attr("x", width / 2)
            .attr("y", height - 4)
            .text("Start Date");


    var yAxis = d3.svg.axis()
            .scale(yScale)
            .orient("left")
            .ticks(5);

    svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + padding.left + ",0)")
            .call(yAxis);

    svg.append("text")
            .attr("class", "y label")
            .attr("text-anchor", "center")
            .attr("x", (-height - padding.bottom) / 2)
            .attr("y", 18)
            .attr("transform", "rotate(-90)")
            .text("Cycle Length (days)");

    // Title
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 35)
        .attr("text-anchor", "middle")
        .attr("class", "h4")
        .text("Cycle Length History");

};
