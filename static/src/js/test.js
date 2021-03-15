odoo.define('openacademy.test', function(require)
{

    var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
    var isFirefox = typeof InstallTrigger !== 'undefined';
    var isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));
    var isIE = /*@cc_on!@*/false || !!document.documentMode;
    var isEdge = !isIE && !!window.StyleMedia;
    var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);
    var isEdgeChromium = isChrome && (navigator.userAgent.indexOf("Edg") != -1);


    var form_widget = require('web.FormRenderer');
    var mobile = require('web_mobile.core');

    form_widget.include({
        _addOnClickAction: function ($el, node) {

            var self = this;
            $el.click(function () {

                if(isFirefox || isChrome || isIE || isSafari || isEdge || isOpera || isEdgeChromium){
                    alert("You should use ODOO application to use this function.");
                }  else {
                    console.log("You are on phone!");
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
                }


            });
        }


    });
});

