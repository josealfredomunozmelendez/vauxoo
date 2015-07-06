from openerp.tests.common import TransactionCase


class TestPrintReport(TransactionCase):

    def setUp(self):
        super(TestPrintReport, self).setUp()
        self.sale = self.registry('sale.order')

    def test_print_report(self):
        cr, uid = self.cr, self.uid
        sale_id = self.sale.search(cr, uid, [], limit=1)
        if sale_id:
            self.assertTrue(self.sale.print_quotation(cr, uid, sale_id),
                            "The report was not generated")
            self.assertTrue(self.sale.action_quotation_send(cr, uid, sale_id),
                            "The action to send the report by mail was "
                            "no open")
