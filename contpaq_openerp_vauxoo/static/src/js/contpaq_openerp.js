openerp.contpaq_openerp_vauxoo = function (instance) {                                                                
var _t = instance.web._t,                                                                              
   _lt = instance.web._lt;                                                                             
var QWeb = instance.web.qweb;

instance.web.form.FieldBinaryBS3 = instance.web.form.FieldBinaryFile.extend({                                   
    template: 'FieldBinaryBS3',
});

instance.web.form.widgets.add('FieldBinaryBS3','instance.web.form.FieldBinaryBS3');                     
}; 
