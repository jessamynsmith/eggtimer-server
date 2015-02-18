makeEvents = function(data) {
    events = Array();

    data.forEach(function(item) {
        var event = {
            title: 'period',
            start: item.start_date,
            period_id: item.id,
            color: '#0f76ed'
        };

        var eventType = item.type;
        if (eventType == 'projected period') {
            event.title = eventType;
            event.color = 'darkred';
        } else if (eventType == 'projected ovulation') {
            event.title = eventType;
            event.color = 'purple';
        } else if (eventType == 'day count') {
            event.title = item.text;
            event.color = '#ffffff';
            event.textColor = '#666666';
            event.editable = false;
        }

        events.push(event);
    });
    return events;
};

getDefaultDate = function(moment, queryString) {
    var startDate = null;
    var endDate = null;
    var defaultDate = null;
    if (queryString && queryString.length) {
        var queries = queryString.substring(1).split("&");
        for (var i=0; i< queries.length; i++) {
            var parts = queries[i].split('=');
            if (parts[0] === "start") {
                startDate = moment(parts[1]);
            }
            if (parts[0] === "end") {
                endDate = moment(parts[1]);
            }
        }
        if (startDate && endDate) {
            defaultDate = startDate + (endDate - startDate) / 2;
        }
    }
    return defaultDate;
};

var initializeCalendar = function(periods_url) {
    $('#calendar').fullCalendar({
        defaultDate: getDefaultDate(moment, window.location.search),
        events: function(start, end, timezone, callback) {
            var startDate = start.format('YYYY-MM-DD');
            var endDate = end.format('YYYY-MM-DD');
            $.ajax({
                url: periods_url,
                dataType: 'json',
                data: {
                    start_date__gte: startDate,
                    start_date__lte: endDate
                },
                success: function(doc) {
                    var newUrl = window.location.protocol + "//" + window.location.host +
                        window.location.pathname + "?start=" + startDate + "&end=" + endDate;
                    window.history.pushState({path:newUrl}, '', newUrl);
                    callback(makeEvents(doc.objects));
                }
            });
        },
        dayClick: function(date, jsEvent, view) {
            var start_date = date.toDate();
            var data = {'start_date': start_date};
            var now = new Date();
            if (start_date == now.getDate()) {
                data.start_time = now.toLocaleTimeString();
            }
            $.ajax({
                url: periods_url,
                contentType: 'application/json',
                type: 'POST',
                data: JSON.stringify(data),
                beforeSend: function(jqXHR, settings) {
                    jqXHR.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                },
                success: function(data, textStatus, jqXHR) {
                    console.log("Period created starting on " + start_date);
                    $('#calendar').fullCalendar( 'refetchEvents' );
                }
            });

        },
        eventClick: function(calEvent, jsEvent, view) {
            var period_id = arguments[0].period_id;
            $.ajax({
                url: periods_url + period_id + '/',
                contentType: 'application/json',
                type: 'DELETE',
                beforeSend: function(jqXHR, settings) {
                    jqXHR.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                },
                success: function(data, textStatus, jqXHR) {
                    console.log("Period " + period_id + " deleted.");
                    $('#calendar').fullCalendar( 'refetchEvents' );
                }
            });
        }
    });
};
