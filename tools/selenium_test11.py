# coding: utf-8
import time
import click

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasicFlow(object):

    def __init__(self, **args):
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.dir", '/tmp')
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                          "application/pdf")
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("pdfjs.disabled", True)
        self.driver = webdriver.Firefox(firefox_profile=fp)
        self.driver.implicitly_wait(15)
        self.product = args.get('product')
        self.partner = args.get('partner')
        self.password = args.get('password')
        self.name = args.get('name')
        self.user = args.get('user')
        self.driver.get('%(server)s/web/login?db=%(db)s' % args)
        time.sleep(3)

    def find(self, element, method=None, wait=10):
        """Find website elements"""
        method = method or By.XPATH
        locator = (method, element)
        return WebDriverWait(self.driver, wait).until(
            EC.presence_of_element_located(locator))
        time.sleep(0.5)

    def sign_in(self):
        """Sign in"""
        driver = self.driver
        time.sleep(1)
        driver.execute_script(
            "$('input#login').val('%s')" % self.user)
        time.sleep(1)
        driver.execute_script(
            "$('input#password').val('%s')" % self.password)
        time.sleep(1)
        driver.execute_script(
            "$('button[type=submit]:contains(Log in)').click()")

    def toggle_home(self):
        """Toggle home screen to be displayed"""
        self.find("//nav/div/a").click()

    def click_outside(self):
        """Used to do click in somewhere in the window to trigger the
        onchange"""
        self.find("div.o_content", By.CSS_SELECTOR).click()

    def go_to_purchase_form(self):
        """Method used to move us from main window to view for of purchase
        order"""
        self.find("Purchases", By.LINK_TEXT).click()
        self.find("//button[normalize-space(text())='Create']").click()

    def fill_form_purchase(self):
        """Fill the form for a new purchase order, testing the onchanges for
        partner and product

        The quantity and the price was modified after the product was loaded
        and the fields computed by onchange method returned, this to verify the
        recompute of the price
        """
        element = self.find("//div[@name='partner_id']/div/input")
        element.clear()
        element.send_keys('asustek')
        time.sleep(1)
        element.send_keys(Keys.RETURN)
        self.click_outside()
        time.sleep(1)
        self.find("Add an item", By.LINK_TEXT).click()
        element = self.find("//div[@name='product_id']/div/input")
        element.clear()
        element.send_keys(self.product)
        time.sleep(1)
        element.send_keys(Keys.RETURN)
        element = self.find("//input[@name='product_qty']")
        element.clear()
        element.send_keys("70000")
        time.sleep(1)
        element = self.find("//input[@name='price_unit']")
        element.clear()
        element.send_keys("100")
        self.click_outside()
        self.find("//button[.='Confirm Order' and not(contains(@class, "
                  "'o_invisible_modifier'))]").click()

    def validate_picking_purchase(self):
        """Used to move us from confirmed purchase order to the delivery order
        generated, then validate its contents"""
        self.find("//div[@name='picking_count']/parent::button").click()
        self.find("//button[.='Validate']").click()
        self.find("//button[@name='process']/span[.='Apply']").click()

    def create_invoice_purchase(self):
        """Then the picking was validated we go ahead to create the invoice
        and then validate it to complete the purchase process for this test"""
        self.find("//div[@name='invoice_count']/parent::button").click()
        time.sleep(1)
        self.find("//button[normalize-space(text())='Create']").click()
        self.find("//button[.='Validate']").click()

    def go_to_sale_form(self):
        """Method used to move us from main window to view for of sale order
        """
        self.find("//button[normalize-space(text())='Create']").click()

    def fill_sale_form(self):
        """Fill the form for a new sale order, testing the onchanges for
        partner and product

        The quantity and the price was modified after the product was loaded
        and the fields computed by onchange method returned, this to verify the
        recompute of the price
        """
        element = self.find("//div[@name='partner_id']/div/input")
        element.clear()
        element.send_keys(self.partner)
        time.sleep(1)
        element.send_keys(Keys.RETURN)
        self.click_outside()
        time.sleep(1)
        element = self.find("//div[@name='pricelist_id']/div/input")
        element.clear()
        element.send_keys("MXN")
        time.sleep(1)
        element.send_keys(Keys.RETURN)
        self.click_outside()
        time.sleep(1)
        self.find("Add an item", By.LINK_TEXT).click()
        element = self.find("//div[@name='product_id']/div/input")
        element.clear()
        element.send_keys(self.product)
        time.sleep(1)
        element.send_keys(Keys.RETURN)
        element = self.find("//input[@name='product_uom_qty']")
        element.clear()
        element.send_keys("10")
        time.sleep(1)
        element = self.find("//input[@name='price_unit']")
        element.clear()
        element.send_keys("150")
        self.find("//button[@class='btn btn-sm btn-primary']/span[1]").click()
        self.find("//button[normalize-space(text())='Confirm Sale' "
                  "and not(contains(@class, 'o_invisible_modifier'))]").click()


    def go_back_to_document(self):
        """Returns to the sale order from the picking form"""
        order = self.find("//span[@name='origin']").text
        self.find("//li/a[.='" + order + "']").click()

    def create_invoice(self):
        """Then the picking was validated we go ahead to create the invoice
        and then validate it to complete thevsale process for this test"""

        self.find("//button[.='Create Invoice' and not(contains(@class, "
                  "'o_invisible_modifier'))]").click()
        self.find("//button[@name='create_invoices']").click()
        self.find("//button[.='Validate']").click()

    def register_payment(self):
        """Register a payment from a Customer Invoive and validate it"""
        self.find("//button[.='Register Payment']").click()
        self.find("//button[@name='action_validate_invoice_payment']").click()

    def update_product(self):
        self.find("Sales", By.LINK_TEXT).click()
        self.find("//li/a[@data-menu-xmlid='sale.product_menu_catalog']").click()
        self.find("//li/a[@data-menu-xmlid='sale.menu_product_template_action']").click()
        self.find("//div[@class='oe_kanban_global_click o_kanban_record']//span[normalize-space(text())='" + self.product + "']").click()
        self.find("//button[normalize-space(text())='Edit']").click()
        self.find("//li/a[normalize-space(text())='Inventory']").click()
        self.find("//label[normalize-space(text())='Buy']").click()
        self.find("//button[normalize-space(text())='Save']").click()
        self.find("//div[@class='o_menu_brand']").click()



@click.command()
@click.option('-server',
              default='',
              prompt='Server',
              help='Url of the server to create connection')
@click.option('-user',
              default='',
              prompt='User',
              help='User to do the login')
@click.option('-password',
              default='',
              prompt='Password',
              help='User to do the login')
@click.option('-db',
              default='',
              prompt='DB',
              help='User to do the login')
@click.option('-com',
              default='',
              prompt='Company',
              help='Company which the test is going  to run the test')
@click.option('-name',
              default='',
              prompt='Name',
              help='Name of user who is going  to run the test')
def main(server, user, password, db, com, name):
    partner = {
        'vauxoo': 'Colima',
    }
    product = {
        'vauxoo': 'Ice Cream',
    }
    values = {
        'server': server,
        'user': user,
        'password': password,
        'db': db,
        'partner': partner.get(com),
        'product': product.get(com),
        'name': name
    }

    basic_list = ['sign_in', 'go_to_purchase_form', 'fill_form_purchase',
                  'validate_picking_purchase', 'go_back_to_document',
                  'create_invoice_purchase', 'register_payment', 'toggle_home',
                  'update_product', 'go_to_sale_form', 'fill_sale_form',
                  'create_invoice', 'register_payment', 'toggle_home']
    methods = {
        'vauxoo': basic_list,
    }

    sale = BasicFlow(**values)
    for method in methods.get(com, basic_list):
        getattr(sale, method)()
        time.sleep(3)


if __name__ == '__main__':
    main()
