odoo.define('vauxoo.dashboard', function (require) {
"use strict";
//
//var core = require('web.core');
//var formats = require('web.formats');
//var Model = require('web.Model');
//var session = require('web.session');
//var KanbanView = require('web_kanban.KanbanView');
//var data = require('web.data');
//
//var QWeb = core.qweb;
//
//var _t = core._t;
//var _lt = core._lt;
//
//
//var GlobalDashboard = KanbanView.extend({
//    display_name: _lt('Dashboard'),
//    icon: 'fa-dashboard',
//    searchview_hidden: true,
//
//    fetch_data: function() {
//        // Overwrite this function with useful data
//        return $.when();
//    },
//
//    render: function() {
//        var super_render = this._super;
//        var self = this;
//
//        return this.fetch_data().then(function(result){
//            self.show_demo = result && result.nb_opportunities === 0;
//
//            var sales_dashboard = QWeb.render('sales_team.SalesDashboard', {
//                widget: self,
//                show_demo: self.show_demo,
//                values: result,
//            });
//            super_render.call(self);
//            $(sales_dashboard).prependTo(self.$el);
//        });
//    },
//});
//
//core.view_registry.add('global_dashboard', GlobalDashboard);
//
//return GlobalDashboard;
};
