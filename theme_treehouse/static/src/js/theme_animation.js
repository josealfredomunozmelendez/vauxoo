odoo.define('theme_treehouse.animation', function (require) {
    'use strict';

    var base = require('web_editor.base');

    base.ready().then(function () {
        // Back to Top
        $('#copyright .top').click(function () {
            $('html, body').animate({scrollTop : 0}, 800);
            return false;
        });

        // Dropdown SHOW
        $('.dropdown, .btn-group').on('show.bs.dropdown', function (e) {
            $(this).find('.dropdown-menu').first().stop(true, true).slideDown();
        });

        //  Dropdown HIDE
        $('.dropdown, .btn-group').on('hide.bs.dropdown', function (e) {
            e.preventDefault();
            $(this).find('.dropdown-menu').first().stop(true, true).slideUp('', function () {
                $(this).parent().removeClass('open');
            });
        });
    });
});
