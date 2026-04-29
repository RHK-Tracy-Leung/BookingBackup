import logging
import requests
import hashlib
from urllib.parse import urlencode
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentProviderQFPay(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('qfpay', 'QFPay')],
        ondelete={'qfpay': 'set default'}
    )
    qfpay_appcode = fields.Char('QFPay AppCode', default='FB02103497894543BA10093AE16640B5')
    qfpay_secret_key = fields.Char('QFPay Secret Key', default='7205D02453A64FE58407F87AB043C764')
    qfpay_sign_type = fields.Selection([('sha256', 'SHA256'), ('md5', 'MD5')], string="Sign Type", default='sha256')
    qfpay_paysource = fields.Char('Paysource', default='remotepay_checkout')
    qfpay_store_id = fields.Char('QFPay Store ID', default='1234567890')

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.code != 'qfpay':
            return super()._get_supported_currencies()

        return self.env['res.currency'].search([
            ('name', '=', 'CNY'),
            ('active', '=', True)
        ])

    def _compute_feature_support_fields(self):
        """启用退款和二维码"""
        res = super()._compute_feature_support_fields()
        for provider in self:
            if provider.code == 'qfpay':
                provider.support_refund = 'partial'
                provider.support_tokenization = False
        return res

    # ==============================
    # 支付请求
    # ==============================
    def _qfpay_generate_sign(self, params):
        """生成签名：MD5(params + key)"""
        sorted_params = '&'.join(f"{k}={v}" for k, v in sorted(params.items()) if v)
        sign_str = f"{sorted_params}&key={self.qfpay_api_key}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def _qfpay_make_request(self, endpoint, payload):
        url = f"https://gateway.qfapi.com{endpoint}"
        _logger.info("Sending QFPay request: %s", payload)

        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()

    def _get_processing_values(self, tx):
        """创建预支付订单"""
        res = super()._get_processing_values(tx)
        base_url = self.get_base_url()

        payload = {
            'appcode': acquirer.qfpay_appcode,
            'sign_type': acquirer.qfpay_sign_type,
            'paysource': acquirer.qfpay_paysource,
            'mchntid': acquirer.qfpay_store_id,
            'order_no': tx.reference,
            'amount': int(tx.amount * 100),  # 单位：分
            'currency': 'CNY',
            'notify_url': f"{base_url}/payment/qfpay/notify",
            'return_url': tx.get_portal_url(),
            'subject': f"Order {tx.reference}",
            'body': "Online Payment",
            'pay_type': 'WX_BARCODE',  # 可改为 ALI_BARCODE
            'timestamp': fields.Datetime.now().strftime('%Y%m%d%H%M%S'),
        }

        # 添加签名
        payload['sign'] = self._qfpay_generate_sign(payload)

        try:
            resp = self._qfpay_make_request('/pay/unified_order', payload)
            if resp.get('result_code') == '0':
                tx.write({
                    'acquirer_reference': resp.get('trade_no'),
                })
                qr_code_url = resp.get('code_url')
                if qr_code_url:
                    return {
                        **res,
                        'qr_code_url': qr_code_url,
                    }
            else:
                raise UserError(f"QFPay Error: {resp.get('err_msg')}")
        except Exception as e:
            _logger.exception("QFPay request failed")
            raise UserError(_("Unable to connect to QFPay gateway."))


