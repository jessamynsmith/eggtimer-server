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

makeEvents = function(data) {
    events = Array();

    data.forEach(function(item) {
        var event = {
            title: 'period',
            itemId: item.id,
            itemType: item.type,
            start: item.start_date,
            color: '#0f76ed',
            // Maybe someday allow dragging of period events
            editable: false
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
        } else {
            var startTime = item.start_time;
            if (!startTime) {
                startTime = '00:00:00';
            }
            event.start = makeDateTimeString(item.start_date, startTime);
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
            $('#id_calendar').fullCalendar( 'refetchEvents' );
        }
    });
};

editEvent = function(action, periodsUrl, itemId, itemDate) {
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
            var data = {start_date: $('#id_start_date').val()};
            var startTime = $('#id_start_time').val();
            if (startTime) {
                data.start_time  = startTime;
            }
            doAjax(periodsUrl, method, itemId, data);
            dialogRef.close();
        }
    });
    BootstrapDialog.show({
        title: action + ' event',
        message: function(dialog) {
            return $('<label for="id_start_date">Start Date:</label>' +
            '<input id="id_start_date" type="text" class="form-control width_form_control" ' +
            'value="' + formatMomentDate(itemDate) + '">' +
            '<label for="id_start_time">Start Time:</label>' +
            '<input id="id_start_time" type="text" class="form-control width_form_control" ' +
            'value="' + formatMomentTime(itemDate) + '" placeholder="00:00">');
        },
        onshown: function(dialog) {
            $('#id_start_date').datepicker({dateFormat: 'yy-mm-dd'});
        },
        closable: true,
        buttons: buttons
    });
};

var initializeCalendar = function(periodsUrl) {
    $('#id_calendar').fullCalendar({
        defaultDate: getDefaultDate(moment, window.location.search),
        events: function(start, end, timezone, callback) {
            var startDate = formatMomentDate(start);
            var endDate = formatMomentDate(end);
            $.ajax({
                url: periodsUrl,
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
            var dayMoment = moment(date);
            var now = moment();
            if (dayMoment.date() == now.date()) {
                // If the entry is for the current day, populate time
                dayMoment = now;
            }
            editEvent('Add', periodsUrl, null, dayMoment);
        },
        eventClick: function(event, jsEvent, view) {
            // Right now, periods do not have a type. This will change when I add spotting.
            editEvent('Update', periodsUrl, event.itemId, event.start);
        }
    });
};
