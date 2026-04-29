# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval
from odoo.addons.whatsapp.tools import phone_validation as wa_phone_validation
from bs4 import BeautifulSoup
import html

class BookingStatistics(models.Model):
    _name = 'booking.statistics'

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string="Product")

    teacher_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Teacher")

    teacher_user_id = fields.Many2one(
        comodel_name='res.users',
        string="Teacher")

    product_uom_qty = fields.Integer(string="Product Uom Qty")

    income = fields.Monetary(string="Income", readonly=True)

    currency_id = fields.Many2one(comodel_name='res.currency', compute='_compute_currency_id')

    def _compute_currency_id(self):
        self.currency_id = self.env.company.currency_id

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        domain.append(('teacher_user_id', '=', self.env.user.id))
        data = super().web_search_read(domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit)
        return data

    # @property
    # def _table_query(self):
    #     return self._query()
    #
    # def _query(self):
    #     with_ = ""
    #     return f"""
    #         {"WITH" + with_ + "(" if with_ else ""}
    #         SELECT {self._select_sale()}
    #         FROM {self._from_sale()}
    #         WHERE {self._where_sale()}
    #         {")" if with_ else ""}
    #     """
    #
    # def _select_sale(self):
    #     select_ = f"""
    #
    #         '1' AS product_template_id,
    #         s.partner_id AS teacher_partner_id,
    #         '23' AS income"""
    #
    #     return select_
    #
    # def _from_sale(self):
    #     return """
    #         sale_order s
    #         """
    #
    # def _where_sale(self):
    #     return """"""
