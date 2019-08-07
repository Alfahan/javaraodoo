from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return


class SaleTarget(models.Model):
    _name = 'sale.target'
    _description = 'Sales Target'

    name = fields.Char(string='Name')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    amount_actual = fields.Float(string='Actual', compute='_get_actual')
    amount_target = fields.Float(string='Target')
    percentage = fields.Float(string='(%)', compute='_get_actual')

    @api.multi
    @api.depends('date_from', 'date_to', 'amount_target')
    def _get_actual(self):
        for target in self:
            if target.date_from and target.date_to:
                domain = [
                    ('state', 'in', ['sale', 'done']),
                    ('confirmation_date', '>=', target.date_from),
                    ('confirmation_date', '<=', target.date_to),
                ]
                sales = self.env['sale.order'].search(domain)
                if sales:
                    amount_actual = sum(sales.mapped('amount_total'))
                    target.amount_actual = amount_actual

            amount_target = target.amount_target
            target.parcentage = amount_actual / amount_target if amount_target > 0 else 0
