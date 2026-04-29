# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError, AccessError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_date = fields.Datetime(
        string="Invoice Date", compute='_get_invoice_date', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        order = super().create(vals_list)
        # order._calc_booking_statistics()
        return order

    def write(self, values):
        result = super().write(values)
        # self._calc_booking_statistics()
        return result

    def _calc_booking_statistics(self):
        for order in self:
            if order.state not in ['draft', 'cancel', 'sent']:
                order.order_line._calc_booking_statistics()
    @api.depends('invoice_ids')
    def _get_invoice_date(self):
        for order in self:
            if order.invoice_ids and len(order.invoice_ids) > 0:
                order.invoice_date = order.invoice_ids.sorted(key='invoice_date', reverse=True)[0].invoice_date
            else:
                order.invoice_date = None


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        # lines._calc_booking_statistics()
        return lines

    def write(self, values):
        result = super().write(values)
        # self._calc_booking_statistics()
        return result

    def unlink(self):
        result = super().unlink()
        # self._calc_booking_statistics()
        return result

    def _calc_booking_statistics(self):
        for line in self:
            if line.product_template_id.teacher_user_id:
                same_product_lines = self.env['sale.order.line'].search([('product_template_id', '=', line.product_template_id.id), ('order_id.state', 'not in', ['draft', 'cancel', 'sent'])])
                income = 0.0
                product_uom_qty = 0
                for l in same_product_lines:
                    income = income + (l.price_subtotal - l.product_uom_qty * line.product_template_id.standard_price )
                    product_uom_qty = product_uom_qty + l.product_uom_qty
                statistics = self.env['booking.statistics'].search([('product_template_id', '=', line.product_template_id.id)], limit=1)
                if statistics:
                    statistics[0].income = income
                    statistics[0].product_uom_qty = product_uom_qty
                else:
                    self.env['booking.statistics'].create({
                        'product_template_id': line.product_template_id.id,
                        'teacher_user_id': line.product_template_id.teacher_user_id.id,
                        'income': income,
                        'product_uom_qty': product_uom_qty
                    })
