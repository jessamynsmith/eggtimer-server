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
            var data = Array({id: '1', type: 'period', start_date: '2015-01-01'});
            var result = makeEvents(data);
            assert.equal(1, result.length);
            assert.equal("period", result[0].title);
            assert.equal("2015-01-01", result[0].start);
            assert.equal("#0f76ed", result[0].color);
        });
    })
});
