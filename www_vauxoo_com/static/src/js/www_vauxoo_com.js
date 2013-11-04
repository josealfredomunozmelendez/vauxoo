openerp.www_vauxoo_com = function (instance) {
    instance.web.UserMenu.include({
    /**
     * This hacking is only to overwrite some widets to addapt to our look and feel, no logic should
     * be here the user menu was mixed with dropdown feature, we removed this class and add our own
     * not related with dropdown.
     */
        start: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.$el.on('click', '.oe_user_menu_bs3 li a[data-menu]', function(ev) {
                ev.preventDefault();
                var f = self['on_menu_' + $(this).data('menu')];
                if (f) {
                    f($(this));
                }
            });
        }
    });
    /**
     * This hacking is only to overwrite some widets to addapt to our look and feel, no logic should
     * be here
    instance.hr_attendance.AttendanceSlider.include({
        start: function() {
            var self = this;
            var tmp = function() {
                this.$el.toggleClass("oebs3_attendance_nosigned", ! this.get("signed_in"));
                this.$el.toggleClass("oebs3_attendance_signed", this.get("signed_in"));
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
     */
};
