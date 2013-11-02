
openerp.www_vauxoo_com = function (instance) {
    /**
     * This hacking is only to overwrite some widets to addapt to our look and feel, no logic should
     * be here
     */
    instance.hr_attendance.AttendanceSlider.include({
        start: function() {
            var self = this;
            var tmp = function() {
                this.$el.toggleClass("oe_attendance_nosigned", ! this.get("signed_in"));
                this.$el.toggleClass("oe_attendance_signed", this.get("signed_in"));
            };
            this.on("change:signed_in", this, tmp);
            _.bind(tmp, this)();
            this.$(".oebs3_attendance_signin").click(function() {
                self.do_update_attendance();
            });
            this.$(".oebs3_attendance_signout").click(function() {
                self.do_update_attendance();
            });
            this.$el.tipsy({
                title: function() {
                    var last_text = instance.web.format_value(self.last_sign, {type: "datetime"});
                    var current_text = instance.web.format_value(new Date(), {type: "datetime"});
                    var duration = self.last_sign ? $.timeago(self.last_sign) : "none";
                    if (self.get("signed_in")) {
                        return _.str.sprintf(_t("Last sign in: %s,<br />%s.<br />Click to sign out."), last_text, duration);
                    } else {
                        return _.str.sprintf(_t("Click to Sign In at %s."), current_text);
                    }
                },
                html: true,
            });
            return this.check_attendance();
        },
    });
    instance.web.UserMenu.include({
        /**
         * Button attendance was included not generically -append- only -prepend- wich bring look
         * and feel incompatibilities.
         */
        do_update: function () {
            this._super();
            var self = this;
            this.update_promise.done(function () {
                if (!_.isUndefined(self.attendanceslider)) {
                    return;
                }
                // check current user is an employee
                var Users = new instance.web.Model('res.users');
                Users.call('has_group', ['base.group_user']).done(function(is_employee) {
                    if (is_employee) {
                        self.attendanceslider = new instance.hr_attendance.AttendanceSlider(self);
                        self.attendanceslider.prependTo(instance.webclient.$('.oe_systray'));
                    } else {
                        self.attendanceslider = null;
                    }
                });
            });
        },
    });
};
