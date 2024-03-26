from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ActivitySale(models.Model):
    _name = "sale.activity"
    _description = "Sale Activity Analysis"

    users_id = fields.Many2one('res.users', 'Salesperson', required=True)
    num_quotations = fields.Integer("Number of Quotations")
    total_amount_quotations = fields.Float("Total Quotation Amount")
    total_num_invoices = fields.Integer("Total Number of Invoices")
    num_invoices = fields.Integer("Number of Invoices Paid")
    unpaid_invoices = fields.Integer("Number of Unpaid Invoices")
    total_amount_invoice = fields.Float("Total Amount of Invoices")
    amount_received = fields.Float("Total Amount Received")
    end_date = fields.Datetime('End')
    start_date = fields.Datetime('Start')

    @api.model
    def create(self, vals):
        existing_record = self.env['sale.activity'].search([('users_id', '=', vals.get('users_id'))])
        if existing_record:
            raise ValidationError("You cannot add the same user multiple times.")
        return super(ActivitySale, self).create(vals)

    @api.onchange('users_id')
    def onchange_users_edit(self):
        if self._origin:
            for record in self:
                if record.users_id and record.users_id != record._origin.users_id:
                    raise ValidationError("The Salesperson field cannot be changed once set.")

    @api.depends('users_id', 'start_date', 'end_date')
    def _compute_values_between_dates(self, start_date, end_date):
        for activity in self:
            if activity.users_id:
                # Calculate number of quotations between start_date and end_date
                num_sent_quotations = self.env['sale.order'].search_count([
                    ('user_id', '=', activity.users_id.id),
                    ('state', 'in', ['sale']),
                    ('date_order', '>=', start_date),
                    ('date_order', '<=', end_date)
                ])
                activity.num_quotations = num_sent_quotations

                # Calculate total amount of quotations between start_date and end_date
                sale_orders = self.env['sale.order'].search([
                    ('user_id', '=', activity.users_id.id),
                    ('state', 'in', ['sale']),
                    ('date_order', '>=', start_date),
                    ('date_order', '<=', end_date)
                ])

                total_amount = sum(order.amount_total for order in sale_orders)
                activity.total_amount_quotations = total_amount


                # Calculate total number of invoices between start_date and end_date
                num_total_invoices = self.env['account.move'].search_count([
                    ('invoice_user_id', '=', activity.users_id.id),
                    ('invoice_date', '>=', start_date),
                    ('invoice_date', '<=', end_date)
                ])
                activity.total_num_invoices = num_total_invoices

                num_sent_invoices = self.env['account.move'].search_count([
                    ('invoice_user_id', '=', activity.users_id.id),
                    ('payment_state', '=', 'paid'),
                    ('invoice_date', '>=', activity.start_date),
                    ('invoice_date', '<=', activity.end_date)
                ])
                activity.num_invoices = num_sent_invoices

                num_unpaid_invoices = self.env['account.move'].search_count([
                    ('invoice_user_id', '=', activity.users_id.id),
                    ('state', '=', 'posted'),
                    '|',
                    ('payment_state', '=', 'not_paid'),
                    ('payment_state', '=', 'partial'),
                    ('invoice_date', '>=', activity.start_date),
                    ('invoice_date', '<=', activity.end_date)
                ])
                activity.unpaid_invoices = num_unpaid_invoices

                invoices = self.env['account.move'].search([
                    ('invoice_user_id', '=', activity.users_id.id),
                    ('invoice_date', '>=', activity.start_date),
                    ('invoice_date', '<=', activity.end_date)
                ])
                total_amount = sum(invoice.amount_total_signed for invoice in invoices)
                activity.total_amount_invoice = total_amount

                received = self.env['account.move'].search([
                    ('invoice_user_id', '=', activity.users_id.id),
                    ('payment_state', 'in', ('paid', 'partial')),
                    ('invoice_date', '>=', activity.start_date),
                    ('invoice_date', '<=', activity.end_date)
                ])
                total_amount = sum(invoice.amount_total_in_currency_signed for invoice in received)
                due_amount = sum(invoice.amount_residual_signed for invoice in received)
                received_amount = total_amount - due_amount
                activity.amount_received = received_amount



            else:
                activity.num_quotations = 0
                activity.total_amount_quotations = 0.0
                activity.total_num_invoices = 0
                activity.num_invoices = 0
                activity.unpaid_invoices = 0
                activity.total_amount_invoice = 0
                activity.amount_received = 0

    def action_send_mail(self):

        template = self.env.ref('sale_report.sale_analysis_mail_template')
        activities = self.env['sale.activity'].search([])
        for activity in activities:
            end_date = datetime.now()
            activity.end_date = end_date
            start_date = datetime.now() - timedelta(days=7)
            activity.start_date = start_date
            activity._compute_values_between_dates(start_date, end_date)
            template.send_mail(activity.id, force_send=True)

    def send_mail_for_current_record(activity):
        template = activity.env.ref('sale_report.sale_analysis_mail_template')
        end_date = activity.end_date
        activity.end_date = end_date
        start_date = activity.start_date
        activity.start_date = start_date
        activity._compute_values_between_dates(start_date, end_date)
        template.send_mail(activity.id, force_send=True)
