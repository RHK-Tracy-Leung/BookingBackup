{
    'name': 'QFPay Payment Acquirer',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Accept payments via QFPay (WeChat, Alipay)',
    'depends': ['payment'],
    'data': [
        'views/payment_qfpay_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
