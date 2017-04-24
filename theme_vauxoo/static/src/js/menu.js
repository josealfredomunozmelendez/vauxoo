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

    // make al in page links scroll smoothly
    $('a.smoothly').click(function(){
        $('html, body').animate({
            scrollTop: $( $(this).attr('href') ).offset().top
        }, 500);
        return false;
    });

    // enable popovers
    $('[data-toggle="popover"]').popover();

    // make the menu sticky change color if background is transparent.
    var connected = $("#oe_main_menu_navbar");
    // if the user is logged then margin-top increases due sticky bar of the
    // website editor
    if(connected.length){
        $(".sticky-header").addClass('mt46');
    }
    $(window).scroll(function() {
        if ($(window).scrollTop() >= 100)  {
            $('.sticky-header').addClass('black_header').removeClass('hidden-header');
        }
        else {
            $('.sticky-header').addClass('hidden-header');
        }
    });
});
