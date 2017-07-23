odoo.define('theme_vauxoo.apps', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
    var website = require('website.website');
    var Widget = require('web.Widget');
    if(!$('.app-check').length) {
        return $.Deferred().reject("DOM doesn't contain a app button check");
    }
    var App = Widget.extend({
        events: {
            'click .app-check' : 'onClick',
        },
        init: function(parent){
            this._super(parent);
        },
        start: function(){
            console.log('Started My App');

            return this._super.apply(this, arguments);
        },
        onClick: function(){
            var input = this.$('.app-check');
            console.log(input.data());
            console.log('Hello Widget clicked');
        }
    });
    $('#on_premise_apps').ready(function() {
        // TODO : make it work. For now, once the iframe is loaded, the value of #page_count is
        // still now set (the pdf is still loading)
        new App($(this)).setElement($('.app'));
    });
});
