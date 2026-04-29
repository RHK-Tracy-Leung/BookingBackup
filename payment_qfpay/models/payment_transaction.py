# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from werkzeug import urls

from odoo import _, models
from odoo.exceptions import ValidationError
import hashlib
import uuid
from urllib.parse import quote
from datetime import datetime


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):

        _logger.info("*********************:\n%s", pprint.pformat(processing_values))

        provider = self.env['payment.provider'].browse(processing_values.get('provider_id'))
        _logger.info("------------qfpay_appcode---: %s", provider.qfpay_appcode)

        appcode = provider.qfpay_appcode
        sign_type = 'sha256'
        paysource = 'remotepay_checkout'
        txamt = int(float(processing_values.get('amount')) * 100)
        txcurrcd = 'HKD'
        out_trade_no = processing_values.get('reference')
        txdtm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return_url = 'https://zhngjiashi-booking250908.odoo.com/confirm-email'
        failed_url = 'https://zhngjiashi-booking250908.odoo.com/confirm-email'
        notify_url = 'https://zhngjiashi-booking250908.odoo.com/payment/qfpay/notify'
        goods_name = 'remotfpay_checkout_names'
        udid = str(uuid.uuid4())
        expired_time = '120'
        checkout_expired_time = ''
        limit_pay = ''
        lang = 'zh-cn'
        cancel_url = ''

        params = {
                    'appcode': appcode,
                    'goods_name': goods_name,
                    'out_trade_no': out_trade_no,
                    'paysource': paysource,
                    'return_url': return_url,
                    'failed_url': failed_url,
                    'notify_url': notify_url,
                    'sign_type': sign_type,
                    'txamt': txamt,
                    'txcurrcd': txcurrcd,
                    'txdtm': txdtm
               }

        _logger.info("*********************params:\n%s", pprint.pformat(params))
        params_str = self._param_stringify(params, encode=False)

        # 第二步：计算 SHA256 签名
        sign = self._compute_sha256_sign(params_str, provider.qfpay_secret_key)

        params['sign'] = sign

        # 第三步：生成跳转 URL（参数需 URL 编码）
        encoded_params = self._param_stringify(params, encode=True)
        # Extract the payment link URL and embed it in the redirect form.
        rendering_values = {
            'api_url': 'https://test-openapi-hk.qfapi.com/checkstand/#/?' + encoded_params
        }
        return rendering_values

    def _compute_sha256_sign(self, params_str, api_key):
        """计算签名：sha256(params + api_key)"""
        data = f"{params_str}{api_key}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _param_stringify(self, data, encode=False):
        """
        将字典转换为排序后的查询字符串（类似 JS 的 paramStringify）
    
        :param data: dict - 要转换的字典
        :param encode: bool - 是否对值进行 URL 编码（相当于 encodeURIComponent）
        :return: str - 拼接后的 query string
        """
        if not data:
            return ""
    
        # 过滤空值（None、False、"" 等）并按 key 排序
        sorted_items = sorted((k, v) for k, v in data.items() if v)
    
        parts = []
        for k, v in sorted_items:
            if encode:
                parts.append(f"{k}={quote(str(v), safe='')}")
            else:
                parts.append(f"{k}={v}")
    
        return "&".join(parts)
