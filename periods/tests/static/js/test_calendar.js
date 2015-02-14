require('blanket')({
    pattern: function (filename) {
        return !/node_modules/.test(filename);
    }
});

var assert = require("assert");

var calendar = require("../../../static/js/calendar.js");

describe('Array', function () {
    describe('#makeEvents()', function () {
        it('should return empty array if no data', function () {
            var result = makeEvents(Array());
            assert.equal(0, result.length);
        });
        it('should return array of items if data', function () {
            var data = Array(
                {id: '1', type: 'period', start_date: '2015-01-01'},
                {id: '2', type: 'projected period', start_date: '2015-01-28'},
                {id: '3', type: 'projected ovulation', start_date: '2015-01-14'},
                {id: '4', type: 'day count', start_date: '2015-01-01', text: 'Day: 1'}
            );
            var result = makeEvents(data);
            assert.equal(4, result.length);
            var expected = JSON.stringify({title: "period", start: "2015-01-01",
                "period_id": "1", color: "#0f76ed"});
            assert.equal(JSON.stringify(result[0]), expected);
            expected = JSON.stringify({title: "projected period", start: "2015-01-28",
                "period_id": "2", color: "darkred"});
            assert.equal(JSON.stringify(result[1]), expected);
            expected = JSON.stringify({title: "projected ovulation", start: "2015-01-14",
                "period_id": "3", color: "purple"});
            assert.equal(JSON.stringify(result[2]), expected);
            expected = JSON.stringify({title: "Day: 1", start: "2015-01-01", "period_id": "4",
                color: "#ffffff", "textColor": "#666666", "editable": false});
            assert.equal(JSON.stringify(result[3]), expected);
        });
    })
});
