# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    def unlink(self):
        _logger.info('.......MailFollowers....: %s', self.env.user._is_public())
        if self.env.user._is_public():
            return False
        return super().unlink()


