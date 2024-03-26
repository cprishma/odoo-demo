from odoo import models,fields,api,_

class sale_wizard(models.TransientModel):
    _name = 'sale.wizard'
    product_name_ids = fields.One2many('com.wizard','wiz_product_id',string="Product_name_ids")

    def button_confirm(self):
        connect = self.env['sale.order'].browse(self.env.context.get('active_id'))
        ids = []
        wiz_id = []
        for i in self.product_name_ids:
            wiz_id.append(i.wid)
        for i in connect.order_line:
            ids.append(i.id)
        line1 = []
        for i in self.product_name_ids:
            if i.wid not in ids:
                value={
                    'order_id': connect.id,
                    'product_id': i.product_name_id.id,
                    'name': i.description,
                    'product_uom_qty': i.quantity,
                    'price_unit': i.unit_price,
                    'price_subtotal': i.subtotal,
                }
                line1.append(value)
            else:
                order_line = self.env['sale.order.line'].browse(i.wid)
                order_line.write({
                    'product_id':i.product_name_id.id,
                    'name': i.description,
                    'product_uom_qty': i.quantity,
                    'price_unit': i.unit_price,
                    'price_subtotal': i.subtotal,
                })
        self.env['sale.order.line'].create(line1)
        ids_unlink = [i for i in ids if i not in wiz_id]
        print(ids_unlink)
        self.env['sale.order.line'].browse(ids_unlink).unlink()



class sale_order(models.TransientModel):
    _name = 'com.wizard'

    wiz_product_id = fields.Many2one('sale.wizard',string='wiz product')
    product_name_id = fields.Many2one('product.product',string="product")
    description = fields.Char(string="Description")
    quantity = fields.Integer(string="Quantity")
    unit_price = fields.Integer(string="unit_price")
    subtotal = fields.Integer(string="subtotal")
    wid = fields.Integer(string="id")
