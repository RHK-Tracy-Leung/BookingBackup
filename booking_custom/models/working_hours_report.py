# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from datetime import datetime, timedelta


class WorkingHoursReport(models.Model):
    _name = "working.hours.report"
    _description = "Working Hours Report"
    _auto = False

    teacher_user_id = fields.Many2one(
        comodel_name='res.users',
        string="Teacher")

    working_hours = fields.Float(string="Working Hours")

    @api.depends_context('allowed_company_ids')
    def _compute_currency_id(self):
        self.currency_id = self.env.company.currency_id

    def _with_sale(self):
        return ""

    def _select_sale(self):
        select_ = f"""
            p.teacher_user_id AS id,
            p.teacher_user_id AS teacher_user_id,
            sum(sm.quantity * (CASE WHEN p.working_hours IS NOT NULL THEN p.working_hours ELSE 0 END)) AS working_hours"""

        return select_

    def _from_sale(self):
        return """
            product_template p
            LEFT JOIN product_product pp on pp.product_tmpl_id = p.id
            LEFT JOIN stock_move sm on sm.product_id = pp.id
            LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
            """.format(
            teacher_user_id=self.env.user.id
        )

    def _where_sale(self):
        # 获取当前日期
        today = datetime.today()

        # 计算上周五的日期（今天的日期减去7天再加上1天）
        last_friday = today - timedelta(days=today.weekday() + 3)

        # 计算上周一的日期（上周五的日期减去4天）
        last_monday = last_friday - timedelta(days=4)

        last_monday_str = str(last_monday.year) + '-' + str(last_monday.month) + '-' + str(last_monday.day) + ' 00:00:00'

        last_friday_str = str(last_friday.year) + '-' + str(last_friday.month) + '-' + str(last_friday.day) + ' 23:59:59'
        return """
            p.teacher_user_id is not null and sp.state = 'done' and sp.date_done > '{last_monday_str}' and sp.date_done < '{last_friday_str}'""".format(
            last_monday_str=last_monday_str, last_friday_str=last_friday_str
        )

    def _group_by_sale(self):
        return """
            p.teacher_user_id"""

    def _query(self):
        with_ = self._with_sale()
        return f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {self._select_sale()}
            FROM {self._from_sale()}
            WHERE {self._where_sale()}
            GROUP BY {self._group_by_sale()}
            having sum(sm.quantity * (CASE WHEN p.working_hours IS NOT NULL THEN p.working_hours ELSE 0 END)) > 48
            {")" if with_ else ""}
        """

    @property
    def _table_query(self):
        return self._query()
