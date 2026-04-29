# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval
from odoo.addons.whatsapp.tools import phone_validation as wa_phone_validation
from bs4 import BeautifulSoup
import html

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    teacher_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Teacher")

    teacher_user_id = fields.Many2one(
        comodel_name='res.users',
        string="Teacher")

    product_standard_price = fields.Float(string="Product Standard Price")

    working_hours = fields.Float(string="Working Hours")

    def write(self, values):
        result = super().write(values)
        # self._calc_booking_statistics()
        return result

    def _calc_booking_statistics(self):
        for product in self:
            if product.teacher_user_id:
                same_product_lines = self.env['sale.order.line'].search([('product_template_id', '=', product.id)])
                income = 0.0
                for l in same_product_lines:
                    income = income + (l.price_subtotal - l.product_uom_qty * product.standard_price )
                statistics = self.env['booking.statistics'].search([('product_template_id', '=', product.id)], limit=1)
                if statistics:
                    statistics[0].income = income
                    statistics[0].teacher_user_id = product.teacher_user_id.id
                else:
                    self.env['booking.statistics'].create({
                        'product_template_id': product.id,
                        'teacher_user_id': product.teacher_user_id.id,
                        'income': income,
                    })

