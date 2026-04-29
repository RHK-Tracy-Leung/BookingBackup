import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class QFPayController(http.Controller):

    @http.route('/payment/qfpay/notify', type='json', auth='public', methods=['POST'], csrf=False)
    def qfpay_notify(self):
        """异步通知入口"""
        data = request.jsonrequest
        _logger.info("QFPay notify received: %s", data)

        # 提取必要字段
        order_no = data.get('order_no')
        trade_no = data.get('trade_no')
        status = data.get('status')  # paid/cancelled
        sign = data.get('sign')

        if not all([order_no, trade_no, status]):
            return {'result': 'fail', 'msg': 'Missing required fields'}

        # 查找交易
        tx_sudo = request.env['payment.transaction'].sudo().search([('reference', '=', order_no)], limit=1)
        if not tx_sudo:
            return {'result': 'fail', 'msg': 'Transaction not found'}

        # 验证签名（重要！）
        provider = tx_sudo.provider_id
        expected_sign = provider.sudo()._qfpay_generate_sign(data)
        if expected_sign != sign:
            _logger.warning("Invalid signature for QFPay notify")
            return {'result': 'fail', 'msg': 'Invalid signature'}

        # 处理状态
        if status == 'paid' and tx_sudo.state == 'draft':
            tx_sudo._set_done()
            _logger.info("Transaction %s marked as done", tx_sudo.reference)
        elif status == 'cancelled':
            tx_sudo._set_canceled()

        return {'result': 'ok'}
