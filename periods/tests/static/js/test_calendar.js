require('blanket')({
    pattern: function (filename) {
        return !/node_modules/.test(filename);
    }
});

var assert = require("assert");
var moment = require('moment');

var calendar = require("../../../static/js/calendar.js");


describe('String', function () {
    describe('#formatMomentDate()', function () {
        it('should return empty string if no moment provided', function () {
            var result = formatMomentDate(null);
            assert.equal('', result);
        });
        it('should return formatted date if moment provided', function () {
            var result = formatMomentDate(moment("12-28-2014", "MM-DD-YYYY"));
            assert.equal('2014-12-28', result);
        });
    })
});

describe('String', function () {
    describe('#formatMomentTime()', function () {
        it('should return empty string if no moment provided', function () {
            var result = formatMomentTime(null);
            assert.equal('', result);
        });
        it('should return formatted date if moment provided', function () {
            var result = formatMomentTime(moment("2014-12-28T03:33:44"));
            assert.equal('03:33', result);
        });
    })
});

describe('String', function () {
    describe('#makeDateTimeString()', function () {
        it('should return formatted date time string', function () {
            var result = makeDateTimeString("2014-12-28", "03:33");
            assert.equal('2014-12-28T03:33', result);
        });
    })
});

describe('Array', function () {
    describe('#makeEvents()', function () {
        it('should return empty array if no data', function () {
            var result = makeEvents(moment, Array());
            assert.equal(0, result.events.length);
        });
        it('should return array of items if data', function () {
            var data = Array(
                {id: '1', type: 'period', first_day: true, timestamp: '2015-01-01T04:03:00'},
                {id: '2', type: 'projected period', timestamp: '2015-01-28'},
                {id: '3', type: 'projected ovulation', timestamp: '2015-01-14'},
                {id: '4', type: 'period', timestamp: '2015-01-02T00:00:00'}
            );
            var result = makeEvents(moment, data);
            assert.equal(2, result.periodStartDates.length);
            assert.equal('2015-01-01', result.periodStartDates[0].format('YYYY-MM-DD'));
            assert.equal('2015-01-28', result.periodStartDates[1].format('YYYY-MM-DD'));
            assert.equal(4, result.events.length);
            var expected = JSON.stringify({title: "period", "itemId": "1", "itemType": "period",
                start: "2015-01-01T09:03:00.000Z", color: "#0f76ed", "editable": false});
            assert.equal(JSON.stringify(result.events[0]), expected);
            expected = JSON.stringify({title: "projected period", "itemId": "2", "itemType":
                "projected period", start: "2015-01-28T05:00:00.000Z", color: "darkred",
                "editable": false});
            assert.equal(JSON.stringify(result.events[1]), expected);
            expected = JSON.stringify({title: "projected ovulation", "itemId": "3", "itemType":
                "projected ovulation", start: "2015-01-14T05:00:00.000Z", color: "purple",
                "editable": false});
            assert.equal(JSON.stringify(result.events[2]), expected);
            var expected = JSON.stringify({title: "period", "itemId": "4", "itemType": "period",
                start: "2015-01-02T05:00:00.000Z", color: "#0f76ed", "editable": false});
            assert.equal(JSON.stringify(result.events[3]), expected);
        });
    })
});

describe('String', function () {
    describe('#getDefaultDate()', function () {
        it('should return null if no querystring', function () {
            var result = getDefaultDate("");
            assert.equal(null, result);
        });
        it('should return null if only start in querystring', function () {
            var result = getDefaultDate(moment, "?start=2014-12-28");
            assert.equal(null, result);
        });
        it('should return null if only end in querystring', function () {
            var result = getDefaultDate(moment, "?end=2015-02-08");
            assert.equal(null, result);
        });
        it('should return moment if start and date in querystring', function () {
            var result = getDefaultDate(moment, "?start=2014-12-28&end=2015-02-08");
            assert.equal("2015-01-18", moment(result).format("YYYY-MM-DD"));
        });
    })
});
