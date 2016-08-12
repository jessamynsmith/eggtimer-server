formatMoment = function(instance, format) {
    if (instance !== null) {
        return instance.format(format);
    }
    return '';
};

formatMomentDate = function(instance) {
    return formatMoment(instance, 'YYYY-MM-DD');
};

var timezoneDate = function(moment, timezone, dateString) {
    return moment.tz(dateString, timezone);
};

makeEvents = function(moment, timezone, data) {
    var events = [];
    var periodStartDates = [];

    data.forEach(function(item) {
        // TODO say "spotting" for spotting events
        var event = {
            title: 'period',
            itemId: item.id,
            itemType: item.type,
            start: timezoneDate(moment, timezone, item.timestamp),
            color: '#0f76ed',
            // Maybe someday allow dragging of period events
            editable: false
        };

        var eventType = item.type;
        if (eventType == 'projected period') {
            periodStartDates.push(event.start);
            event.title = eventType;
            event.color = 'darkred';
        } else if (eventType == 'projected ovulation') {
            event.title = eventType;
            event.color = 'purple';
        } else {
            if (item.first_day) {
                event.title = '*' + event.title;
                periodStartDates.push(event.start);
            }
        }

        events.push(event);
    });
    return {events: events, periodStartDates: periodStartDates};
};

addDayCounts = function(periodStartDates, firstDate, firstDay) {
    $('.day-count').remove();
    if (!firstDay) {
        console.log("No days to add");
        return;
    }
    var currentDay = firstDay;
    var nextPeriodStart = periodStartDates.shift();
    $('.fc-day-number').each(function() {
        var currentDate = moment($(this).attr('data-date'));
        if (currentDate >= firstDate) {
            if (currentDate.isSame(nextPeriodStart, 'day')) {
                nextPeriodStart = periodStartDates.shift();
                currentDay = 1;
            }
            $(this).append("<p class='day-count'>" + currentDay + "</p>");
            currentDay += 1;
        }
    });
};

getDefaultDate = function(moment, queryString) {
    var startDate = null;
    var endDate = null;
    var defaultDate = null;
    if (queryString && queryString.length) {
        var queries = queryString.substring(1).split("&");
        for (var i = 0; i < queries.length; i++) {
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

doAjax = function(url, method, itemId, data) {
    console.log("Calling " + method + " on item " + itemId + " ...");
    if (itemId !== null) {
        url += itemId + '/';
    }
    $.ajax({
        url: url,
        contentType: 'application/json',
        type: method,
        data: JSON.stringify(data),
        beforeSend: function(jqXHR, settings) {
            jqXHR.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
        },
        success: function(data, textStatus, jqXHR) {
            console.log(method + " on " + itemId + " succeeded");
            $('#id_calendar').fullCalendar('refetchEvents');
        }
    });
};

editEvent = function(action, timezone, periodsUrl, periodFormUrl, itemId, itemDate) {
    var method = 'POST';
    var buttons = [];
    if (action === 'Update') {
        method = 'PUT';
        buttons.push({
            id: 'btn-delete',
            label: 'Delete',
            cssClass: 'btn-warning',
            action: function(dialogRef) {
                BootstrapDialog.confirm('Are you sure you want to delete this event?', function(result) {
                    if (result) {
                        doAjax(periodsUrl, 'DELETE', itemId, {});
                        dialogRef.close();
                    }
                });
            }
        });
    }
    buttons.push({
        id: 'btn-cancel',
        label: 'Cancel',
        cssClass: 'btn-cancel',
        autospin: false,
        action: function(dialogRef) {
            dialogRef.close();
        }
    }, {
        id: 'btn-ok',
        label: action,
        cssClass: 'btn-primary',
        action: function(dialogRef) {
            var data = $("#id_period_form").serializeJSON();
            // drf doesn't recognize 'on'
            data.first_day = data.first_day == 'on';
            // Must convert timestamp to UTC since that is what server is expecting
            var localTimestamp = moment.tz(data.timestamp, timezone);
            data.timestamp = localTimestamp.tz('UTC').format();
            doAjax(periodsUrl, method, itemId, data);
            dialogRef.close();
        }
    });
    BootstrapDialog.show({
        title: action + ' event',
        message: function(dialog) {
            var message = '';
            if (itemId) {
                periodFormUrl += itemId + '/';
            }
            if (itemDate) {
                periodFormUrl += '?timestamp=' + itemDate.format();
            }
            console.log("Getting period form from url: " + periodFormUrl);
            $.ajax({
                url: periodFormUrl,
                dataType: 'html',
                async: false,
                success: function(doc) {
                    message = $('<div></div>').append($(doc));
                }
            });
            return message;
        },
        onshown: function(dialog) {
            addFormStyles();
        },
        closable: true,
        buttons: buttons
    });
};

var makeMoonPhaseEvents = function(responseData, moment, timezone) {
    var events = [];
    console.log(responseData);
    for (var i = 0; i < responseData.length; i++) {
        var event = {
            title: responseData[i].name,
            start: timezoneDate(moment, timezone, responseData[i].dateTimeISO),
            allDay: true,
            className: 'moon ' + responseData[i].name.replace(' ', '_'),
            rendering: 'background'
        };
        events.push(event);
    }
    return events;
};

var initializeCalendar = function(periodsUrl, statisticsUrl, periodFormUrl, aerisUrl, timezone) {
    $('#id_calendar').fullCalendar({
        timezone: timezone,
        defaultDate: getDefaultDate(moment, window.location.search),
        events: function(start, end, timezone, callback) {
            var startDate = formatMomentDate(start);
            var endDate = formatMomentDate(end);
            var data = {
                min_timestamp: startDate,
                max_timestamp: endDate
            };
            $.getJSON(periodsUrl, data, function(periodData) {
                var newUrl = window.location.protocol + "//" + window.location.host +
                    window.location.pathname + "?start=" + startDate + "&end=" + endDate;
                window.history.pushState({path: newUrl}, '', newUrl);
                $.getJSON(statisticsUrl, {min_timestamp: startDate}, function(statisticsData) {
                    var events = makeEvents(moment, timezone, periodData.concat(statisticsData.predicted_events));
                    addDayCounts(events.periodStartDates, moment(statisticsData.first_date),
                        statisticsData.first_day);
                    // TODO Fetch and add these events later, after calendar has rendered
                    $.getJSON(aerisUrl, data, function(aerisData) {
                        if (aerisData.error) {
                            console.log(JSON.stringify(aerisData.error));
                        } else {
                            events.events = events.events.concat(makeMoonPhaseEvents(aerisData.response, moment, timezone));
                        }
                        callback(events.events);
                    });
                });
            });
        },
        dayClick: function(date, jsEvent, view) {
            var dayMoment = moment(date, timezone);
            var now = moment.tz(moment(), timezone);
            if (dayMoment.date() == now.date()) {
                // If the entry is for the current day, populate time
                dayMoment = now;
            }
            editEvent('Add', timezone, periodsUrl, periodFormUrl, null, dayMoment);
        },
        eventClick: function(event, jsEvent, view) {
            if (!event.itemId) {
                // This can happen if the user clicks on a projected event
                return;
            }
            editEvent('Update', timezone, periodsUrl, periodFormUrl, event.itemId, null);
        }
    });
};
