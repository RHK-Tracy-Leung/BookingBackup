# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from odoo.addons.sale.models.sale_order import SALE_ORDER_STATE


class SaleReportCustom(models.Model):
    _name = "sale.report.custom"
    _description = "Sales Analysis Report"
    _auto = False

    # sale.order fields
    # name = fields.Char(string="Order Reference", readonly=True)
    date = fields.Datetime(string="Order Date", readonly=True)
    # partner_id = fields.Many2one(comodel_name='res.partner', string="Customer", readonly=True)
    # company_id = fields.Many2one(comodel_name='res.company', readonly=True)
    # pricelist_id = fields.Many2one(comodel_name='product.pricelist', readonly=True)
    # team_id = fields.Many2one(comodel_name='crm.team', string="Sales Team", readonly=True)
    # user_id = fields.Many2one(comodel_name='res.users', string="Salesperson", readonly=True)
    # state = fields.Selection(selection=SALE_ORDER_STATE, string="Status", readonly=True)
    # analytic_account_id = fields.Many2one(
    #     comodel_name='account.analytic.account', string="Analytic Account", readonly=True)
    # invoice_status = fields.Selection(
    #     selection=[
    #         ('upselling', "Upselling Opportunity"),
    #         ('invoiced', "Fully Invoiced"),
    #         ('to invoice', "To Invoice"),
    #         ('no', "Nothing to Invoice"),
    #     ], string="Invoice Status", readonly=True)
    #
    # campaign_id = fields.Many2one(comodel_name='utm.campaign', string="Campaign", readonly=True)
    # medium_id = fields.Many2one(comodel_name='utm.medium', string="Medium", readonly=True)
    # source_id = fields.Many2one(comodel_name='utm.source', string="Source", readonly=True)
    #
    # # res.partner fields
    # commercial_partner_id = fields.Many2one(
    #     comodel_name='res.partner', string="Customer Entity", readonly=True)
    # country_id = fields.Many2one(
    #     comodel_name='res.country', string="Customer Country", readonly=True)
    # industry_id = fields.Many2one(
    #     comodel_name='res.partner.industry', string="Customer Industry", readonly=True)
    # partner_zip = fields.Char(string="Customer ZIP", readonly=True)
    # state_id = fields.Many2one(comodel_name='res.country.state', string="Customer State", readonly=True)
    #
    # # sale.order.line fields
    # order_reference = fields.Reference(string='Related Order', selection=[('sale.order', 'Sales Order')], group_operator="count_distinct")
    #
    # categ_id = fields.Many2one(
    #     comodel_name='product.category', string="Product Category", readonly=True)
    # product_id = fields.Many2one(
    #     comodel_name='product.product', string="Product Variant", readonly=True)
    # product_tmpl_id = fields.Many2one(
    #     comodel_name='product.template', string="Product", readonly=True)
    # product_uom = fields.Many2one(comodel_name='uom.uom', string="Unit of Measure", readonly=True)
    # product_uom_qty = fields.Float(string="Qty Ordered", readonly=True)
    # qty_to_deliver = fields.Float(string="Qty To Deliver", readonly=True)
    # qty_delivered = fields.Float(string="Qty Delivered", readonly=True)
    # qty_to_invoice = fields.Float(string="Qty To Invoice", readonly=True)
    # qty_invoiced = fields.Float(string="Qty Invoiced", readonly=True)
    # price_subtotal = fields.Monetary(string="Untaxed Total", readonly=True)
    # price_total = fields.Monetary(string="Total", readonly=True)
    # untaxed_amount_to_invoice = fields.Monetary(string="Untaxed Amount To Invoice", readonly=True)
    # untaxed_amount_invoiced = fields.Monetary(string="Untaxed Amount Invoiced", readonly=True)
    #
    # weight = fields.Float(string="Gross Weight", readonly=True)
    # volume = fields.Float(string="Volume", readonly=True)
    #
    # discount = fields.Float(string="Discount %", readonly=True, group_operator='avg')
    # discount_amount = fields.Monetary(string="Discount Amount", readonly=True)
    #
    # # aggregates or computed fields
    # nbr = fields.Integer(string="# of Lines", readonly=True)
    currency_id = fields.Many2one(comodel_name='res.currency', compute='_compute_currency_id')

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string="Product")

    teacher_user_id = fields.Many2one(
        comodel_name='res.users',
        string="Teacher")

    product_qty = fields.Integer(string="Product Uom Qty")

    income = fields.Monetary(string="Income", readonly=True)

    @api.depends_context('allowed_company_ids')
    def _compute_currency_id(self):
        self.currency_id = self.env.company.currency_id

    def _with_sale(self):
        return ""

    def _select_sale(self):
        select_ = f"""
            l.id AS id,
            p.id AS product_template_id,
            s.date_order AS date,
            p.teacher_user_id AS teacher_user_id,
            SUM(l.product_uom_qty) AS product_qty,
            SUM(l.price_subtotal
                - l.product_uom_qty * (CASE WHEN p.product_standard_price IS NOT NULL THEN p.product_standard_price ELSE 0 END)
                ) AS income"""

        return select_

    def _from_sale(self):
        return """
            product_template p
            LEFT JOIN product_product pp on pp.product_tmpl_id = p.id
            LEFT JOIN sale_order_line l on l.product_id = pp.id
            LEFT JOIN sale_order s ON s.id=l.order_id
            """.format(
            teacher_user_id=self.env.user.id
            )

    def _where_sale(self):
        return """
            p.teacher_user_id = {teacher_user_id} and s.state not in ('draft', 'cancel', 'sent')""".format(
            teacher_user_id=self.env.user.id
        )

    def _group_by_sale(self):
        return """
            p.id,
            l.id,
            p.teacher_user_id,
            s.date_order"""

    def _query(self):
        with_ = self._with_sale()
        return f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {self._select_sale()}
            FROM {self._from_sale()}
            WHERE {self._where_sale()}
            GROUP BY {self._group_by_sale()}
            {")" if with_ else ""}
        """

    @property
    def _table_query(self):
        return self._query()
