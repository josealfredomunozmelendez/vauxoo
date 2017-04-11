odoo.define('theme_vauxoo.menu', function (require) {
    'use strict';
    var base = require('web_editor.base');
    var core = require('web.core');
    var transparent = $('data#transparency').data('transparent');
    if (transparent){
        $(".black_header").removeClass('black_header').addClass('transparent_header');
    }
    $('#nav-icon1,#nav-icon2,#nav-icon3,#nav-icon4').click(function(){
        $(this).toggleClass('open');
    });
    $('a').click(function(){
        $('html, body').animate({
            scrollTop: $( $(this).attr('href') ).offset().top
        }, 500);
        return false;
    });
});
