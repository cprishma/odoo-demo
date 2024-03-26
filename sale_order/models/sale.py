from odoo import models, fields, api


class saleorder(models.Model):
    _inherit = 'sale.order'

    def action_wizard_form(self):
        target_data = []
        for i in self.order_line:
            target_data.append([0, 0, {
                'wid': i.id,
                'product_name_id': i.product_id.id,
                'description': i.name,
                'quantity': i.product_uom_qty,
                'unit_price': i.price_unit,
                'subtotal': i.price_subtotal,

            }])

        return {
            'name': 'sale order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_name_ids': target_data}
        }





