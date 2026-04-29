# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    def unlink(self):
        _logger.info('.......MailMail....: %s....user_id: %s', self.id, self.env.user.id)
        if self.env.user.id == 1:
            return False
        return super().unlink()


