formatMoment = function(instance, format) {
    if (instance !== null) {
        return instance.format(format);
    }
    return '';
};

formatMomentDate = function(instance) {
    return formatMoment(instance, 'YYYY-MM-DD');
};

formatMomentTime = function(instance) {
    return formatMoment(instance, 'HH:mm');
};

makeDateTimeString = function(date, time) {
    return date + 'T' + time;
};

makeEvents = function(moment, data) {
    events = Array();
    periodStartDates = Array();

    data.forEach(function(item) {
        var start = moment(item.timestamp);
        // TODO say "spotting for spotting events"
        var event = {
            title: 'period',
            itemId: item.id,
            itemType: item.type,
            start: start,
            color: '#0f76ed',
            // Maybe someday allow dragging of period events
            editable: false
        };

        var eventType = item.type;
        if (eventType == 'projected period') {
            periodStartDates.push(start);
            event.title = eventType;
            event.color = 'darkred';
        } else if (eventType == 'projected ovulation') {
            event.title = eventType;
            event.color = 'purple';
        } else {
            if (item.first_day) {
                event.title = '*' + event.title;
                periodStartDates.push(start);
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
    console.log("Adding day counts");
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
            jqXHR.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        },
        success: function(data, textStatus, jqXHR) {
            console.log(method + " on " + itemId + " succeeded");
            $('#id_calendar').fullCalendar('refetchEvents');
        }
    });
};

editEvent = function(action, periodsUrl, periodFormUrl, itemId, itemDate) {
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
    },{
        id: 'btn-ok',
        label: action,
        cssClass: 'btn-primary',
        action: function(dialogRef) {
            var data = $("#id_period_form").serializeJSON();
            // drf doesn't recognize 'on'
            data.first_day = data.first_day == 'on';
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

var initializeCalendar = function(periodsUrl, statisticsUrl, periodFormUrl) {
    $('#id_calendar').fullCalendar({
        defaultDate: getDefaultDate(moment, window.location.search),
        events: function(start, end, timezone, callback) {
            var startDate = formatMomentDate(start);
            var endDate = formatMomentDate(end);
            $.ajax({
                url: periodsUrl,
                dataType: 'json',
                data: {
                    min_timestamp: startDate,
                    max_timestamp: endDate
                },
                success: function(periodData) {
                    var newUrl = window.location.protocol + "//" + window.location.host +
                        window.location.pathname + "?start=" + startDate + "&end=" + endDate;
                    window.history.pushState({path:newUrl}, '', newUrl);
                    $.ajax({
                        url: statisticsUrl,
                        dataType: 'json',
                        data: {
                            min_timestamp: startDate
                        },
                        success: function(statisticsData) {
                            var events = makeEvents(moment, periodData.concat(statisticsData.predicted_events));
                            addDayCounts(events.periodStartDates, moment(statisticsData.first_date),
                                statisticsData.first_day);
                            callback(events.events);
                        }
                    });
                }
            });
        },
        dayClick: function(date, jsEvent, view) {
            var dayMoment = moment(date);
            var now = moment();
            if (dayMoment.date() == now.date()) {
                // If the entry is for the current day, populate time
                dayMoment = now;
            }
            editEvent('Add', periodsUrl, periodFormUrl, null, dayMoment);
        },
        eventClick: function(event, jsEvent, view) {
            // Right now, periods do not have a type. This will change when I add spotting.
            editEvent('Update', periodsUrl, periodFormUrl, event.itemId, event.start);
        }
    });
};
