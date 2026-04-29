# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models

def post_init_hook(env):
    setup_provider(env, 'qfpay')


def uninstall_hook(env):
    reset_payment_provider(env, 'qfpay')
