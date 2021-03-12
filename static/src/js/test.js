odoo.define('openacademy.test', function(require)
{
    var form_widget = require('web.FormRenderer');
    var mobile = require('web_mobile.core');

    form_widget.include({
        _addOnClickAction: function ($el, node) {

            var self = this;
            $el.click(function () {
                mobile.methods.scanBarcode().then(function(code){
            if(code){
                console.log(code);
                mobile.methods.showToast({'message': code["data"]});

                var part1 = "http://192.168.11.108:8013/web#id=";
                var code_id_session = String(code["data"]);
                var part2 = "&action=592&model=openacademy.session&view_type=form&cids=1&menu_id=341";
                var res = part1.concat(code_id_session, part2);
                window.open(res);
            }
            });

            });
        }


    });
});