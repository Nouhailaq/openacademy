odoo.define('openacademy.utils_tests', function (require) {
"use strict";

var utils = require('web.py_utils');
var result = "";

QUnit.module('openacademy', {}, function () {
    QUnit.module('utils');

    QUnit.test("first test", function (assert) {
        assert.expect(1);
        result = "this is the result";
        assert.strictEqual(result, "this result");


    });
});
});