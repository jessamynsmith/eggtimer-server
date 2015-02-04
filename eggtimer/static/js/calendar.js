initializeCalendar = function(periods_url) {
    $('#calendar').fullCalendar({
        events: function(start, end, timezone, callback) {
            $.ajax({
                url: periods_url,
                dataType: 'json',
                data: {
                    start_date__gte: start.format('YYYY-MM-DD'),
                    start_date__lte: end.format('YYYY-MM-DD')
                },
                success: function(doc) {
                    var events = [];
                    $(doc.objects).each(function() {
                        var event = {
                            title: 'period',
                            start: $(this).attr('start_date'),
                            period_id: $(this).attr('id'),
                            color: '#0f76ed'
                        };

                        var eventType = $(this).attr('type');
                        if (eventType == 'projected period') {
                            event.title = eventType;
                            event.color = 'darkred';
                        } else if (eventType == 'projected ovulation') {
                            event.title = eventType;
                            event.color = 'purple';
                        } else if (eventType == 'day count') {
                            event.title = $(this).attr('text');
                            event.color = '#ffffff';
                            event.textColor = '#666666';
                            event.editable = false;
                        }

                        events.push(event);
                    });
                    callback(events);
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
                // The ``X-CSRFToken`` evidently can't be set in the
                // ``headers`` option, so force it here.
                // This method requires jQuery 1.5+.
                beforeSend: function(jqXHR, settings) {
                    // Pull the token out of the DOM.
                    jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
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
                // The ``X-CSRFToken`` evidently can't be set in the
                // ``headers`` option, so force it here.
                // This method requires jQuery 1.5+.
                beforeSend: function(jqXHR, settings) {
                    // Pull the token out of the DOM.
                    jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
                },
                success: function(data, textStatus, jqXHR) {
                    console.log("Period " + period_id + " deleted.");
                    $('#calendar').fullCalendar( 'refetchEvents' );
                }
            });
        }
    });
};
