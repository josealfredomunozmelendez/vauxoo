<!DOCTYPE>
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    %for o in objects :
    <table class="basic_table" width="100%">
        <tr>
            <td width="30%">
                <div  style="float:left;">
                    ${helper.embed_image('jpeg',str(o.company_id.logo),180, auto)}
                </div>
            </td>
            <td style="vertical-align: bottom;">
                <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
                    <tr>
                        <td style="text-align:center;background-color:FFFFFF;">
                            <table width="100%">
                                <tr>
                                    <td class="td_center">
                                        <strong>${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.name.upper() or '' | entity}</strong>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="td_center">
                                        <p class="data_company"><b>${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.partner_invoice_id.vat and o.user_id.company_id.partner_id.vat[2:] or ''| entity}</b></p>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="td_center">
                                        <p class="data_company">${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.street or '' | entity} 
                                        ${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.street2 or '' | entity} 
                                        ${ o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and ('Ext. %s' % (o.user_id.company_id.partner_id.l10n_mx_street3 or '')) or '' | entity}
                                        ${ o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and ('Int. %s' % (o.user_id.company_id.partner_id.l10n_mx_street4 or '')) or '' | entity},</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="td_center">
                                        <p class="data_company">${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.country_id and o.user_id.company_id.partner_id.country_id.name or ''| entity},
                                        ${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.city or ''| entity }, 
                                        ${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.zip or  '' | entity}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="td_center">
                                        <p class="data_company">${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.email or  '' | entity} - 
                                        ${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.phone or  '' | entity} - 
                                        ${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.fax or  ''| entity } - 
                                        ${o.user_id and o.user_id.company_id and o.user_id.company_id.partner_id and o.user_id.company_id.partner_id.mobile or ''| entity }</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <table class="table_column_border table_alter_color_row table_title_bg_color td_center" width="100%">
                            <tr>
                                <th width="33%"><b>FECHA</b></th>
                                <th width="33%"><b>PRESUPUESTO</b></th>
                                <th width="33%"><b>MONEDA</b></th>
                            </tr>
                            <tr>
                                <td class="td_bold">
                                    ${ o.date_order and formatLang( o.date_order, date=True) or '' | entity}
                                </td>
                                <td class="td_bold">
                                    N°: ${ o.name or '' | entity}
                                </td>
                                <td class="td_bold">
                                    ${'%s(%s)'%(o.pricelist_id and o.pricelist_id.currency_id and o.pricelist_id.currency_id.name or '',o.pricelist_id and o.pricelist_id.currency_id and o.pricelist_id.currency_id.symbol or '') }
                                </td>
                            </tr>
                        </table>
                    </tr>
                </table>
            </td>
       </tr>
    </table>
</br> 
    <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
        <tr>
            <th width="40%">CLIENTE</th>
            <th width="40%">CONTACTO</th>
            <th width="20%">ORIGEN/REFERENCIA/REF. CLIENTE</th>
        </tr>
        <tr>
            <td>
                ${ o.partner_id and o.partner_id.name.upper() or '' | entity}
            </td>
            <td>
                SR(A).: ${o.partner_id and o.partner_id.name or '' | entity} TELF.: ${o.partner_id and o.partner_id.phone or '' | entity} FAX.: ${o.partner_id and o.partner_id.fax or '' | entity} CEL.: ${o.partner_id and o.partner_id.mobile or '' | entity} EMAIL:${o.partner_id and o.partner_id.email or '' | entity}
            </td>
            <td class="td_center td_bold">
                ${o.origin or ''| entity} ${ o.name and ('/%s /'%(o.name)) or ''| entity}${ o.client_order_ref or ''| entity}
            </td>
        </tr>
    </table>
    </br>
    <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
        <tr>
            <th width="30%">FACTURAR A</th>
            <th width="30%">ENTREGAR EN</th>
            <th width="20%">T&Eacute;RMINOS DE PAGO <sup>(1)</sup></th>
            <th width="20%">T&Eacute;RMINOS DE ENTREGA <sup>(2)</sup></th>
        </tr>
        <tr>
            <td>
                ${ o.partner_id and o.partner_id.name or '' | entity} 
                RIF.: ${ o.partner_invoice_id and o.partner_invoice_id.vat and o.partner_invoice_id.vat[2:] or "No Hay Suficiente Informacion para Facturar" } Direccion ${o.partner_invoice_id and o.partner_invoice_id.street or '' | entity} 
                ${o.partner_invoice_id and o.partner_invoice_id.street2 or '' | entity}, ${ o.partner_invoice_id and o.partner_invoice_id.city or '' | entity}, ${o.partner_invoice_id and o.partner_invoice_id.state_id.name or '' | entity}, 
                ${o.partner_invoice_id and o.partner_invoice_id.country_id and o.partner_invoice_id.country_id.name or '' | entity}, 
                ${o.partner_invoice_id and o.partner_invoice_id.phone or '' | entity} 
                Contacto: ${o.partner_invoice_id and o.partner_invoice_id.name or '' | entity}
            </td>
            <td>
                ${o.partner_shipping_id and o.partner_shipping_id.name or 'NO APLICA'},
                ${ o.partner_shipping_id and o.partner_shipping_id.street or '' | entity} 
                ${ o.partner_shipping_id and o.partner_shipping_id.street2 or '' | entity},
                ${ o.partner_shipping_id and o.partner_shipping_id.zip or '' | entity}, 
                ${ o.partner_shipping_id and o.partner_shipping_id.city or '' | entity} 
                ${ o.partner_shipping_id and o.partner_shipping_id.state_id.name or '' | entity} 
                ${ o.partner_shipping_id and o.partner_shipping_id.country_id.name or '' | entity}, 
                ${ o.partner_shipping_id and o.partner_shipping_id.phone or '' | entity}
            </td>
            <td class="td_center">
                ${ o.payment_term and o.payment_term.name or '' | entity}
            </td>
            <td>
                ${ o.incoterm and ('%s [%s]'%(  o.incoterm and o.incoterm.name or '',  o.incoterm and o.incoterm.code or ''))}
            </td>
        </tr>
    </table>
</br>
    <section>
        <table class="table_column_border table_alter_color_row table_title_bg_color">
            <tr>
                <th width="10%">
                    CANTIDAD</br>
                    <hr>
                    [ L&Iacute;NEA ]
                </th>
                <th width="70%">
                    [C&Oacute;DIGO] PRODUCTO</br>
                    <hr>
                    DESCRIPCI&Oacute;N</br>
                    <hr>
                    PLAZO DE ENTREGA
                </th>
                <th width="10%">
                    UNIDAD</br>
                    <hr>
                    PRECIO<sup>(4)</sup>
                </th>
                <th width="10%">
                    SUBTOTAL
                </th>
            </tr>
            <tbody>
            %for line in o.order_line :
                <tr>
                    <td class="td_center" valign="top">
                        ${formatLang(line.product_uos and line.product_uos_qty or line.product_uom_qty ,digits=2, grouping=True)}</br>
                        <hr>
                        [ ${line.sequence or '' | entity} ]
                    </td>
                    <td>
                        <b>[${line.product_id and line.product_id.default_code or '' |entity}]${line.product_id and line.product_id.name or '' |entity}</b></br>
                        <hr>
                        <pre>${line.name or '' | entity}</pre>
                        <pre class="pre_description">${line.product_id and line.product_id.description or '' |entity}</pre>
                        <hr>
                        %if not line.delay==0.00:
                            <i>PLAZO DE ENTREGA: ${formatLang(line.delay, digits=2, grouping=True) or '' }${line.delay==0.00 or ''} DÍAS</i></br>
                        %endif
                        <i>${line.delay==0.00 and 'A CONVENIR' or '' | entity}</i>
                    </td>
                    <td class="td_center" valign="top">
                        [ ${line.product_uom and line.product_uom.name or '' |entity} ]
                        <hr>
                        ${formatLang(line.price_unit, digits=2, grouping=True) or '' |entity}
                    </td>
                    <td class="td_amount" valign="top">
                        ${formatLang(line.price_subtotal, digits=2, grouping=True) or '' |entity }
                    </td>
                </tr>
            %endfor
            </tbody>
        </table>
    </section>
    <p style="word-wrap:break-word;"></p>
    <table  width="100%" style="border-collapse:collapse" class="table_only_border_bottom">
        <tr>
            <td width="80%" class="td_without_bottom"></td>
            <td width="5%"  class="sub_total_td">${_('SUBTOTAL')}</td>
            <td width="15%" align="right" class="sub_total_td">${o.pricelist_id and o.pricelist_id.currency_id and o.pricelist_id.currency_id.symbol or '' |entity} ${formatLang(o.amount_untaxed,digits=2, grouping=True)}</td>
        </tr>
        <tr>
            <td class="td_without_bottom"></td>
            <td class="sub_total_td">${_('IVA')}</td>
            <td align="right" class="sub_total_td">${o.pricelist_id and o.pricelist_id.currency_id and o.pricelist_id.currency_id.symbol or '' |entity} ${formatLang(o.amount_tax,digits=2, grouping=True)}</td>
        </tr>
        <tr>
            <td class="td_without_bottom"></td>
            <td class="td_without_bottom total_td">${_('TOTAL')}</td>
            <td align="right" class="td_without_bottom total_td">${o.pricelist_id and o.pricelist_id.currency_id and o.pricelist_id.currency_id.symbol or '' |entity} ${o.pricelist_id and o.pricelist_id.currency_id and o.pricelist_id.currency_id.name or ''} ${formatLang(o.amount_total, digits=2, grouping=True)}</td>
        </tr>
    </table>
     <table class="table_column_border table_alter_color_row table_title_bg_color" width="100%">
            <tr>
                <th>
                    CONDICIONES
                </th>
            </tr>
            <tr>
                <td style="font-size: 6;">
                    %if (o.note):
                        NOTAS:</br>
                        <pre style="font-size: 6;">${o.note and o.note or '' |entity}</pre>
                    %endif
                    %if (o.payment_term and o.payment_term.name) and (o.payment_term and o.payment_term.note):
                        (1) T&Eacute;RMINOS DE PAGO:</br>
                        <pre style="font-size: 6;">${o.payment_term and o.payment_term.name or '' |entity} ${o.payment_term and o.payment_term.note or '' |entity}</pre></br>
                    %endif
                    %if o.incoterm and o.incoterm.description:
                        (2) T&Eacute;RMINOS DE ENTREGA:</br>
                        <pre style="font-size: 6;">${o.incoterm and o.incoterm.description or 'No se ha estipulado términos comerciales de transporte' |entity}</pre></br>
                    %endif
                </td>
            </tr>
    </table>
    </br>
    <center>
        <table class="table_column_border table_alter_color_row table_title_bg_color" width="30%">
            <tr>
                <th>ASESOR DE VENTAS</th>
            </tr>
            <tr>
                <td class="td_bold td_center">
                    %if (o.user_id):
                        ${o.user_id and o.user_id.name and o.user_id.name.upper() or ''|entity}
                    %endif
                </td>
            </tr>
        </table>
    </center>
    <p style="page-break-before: always;"></p>

    %endfor

</body>
</html>
