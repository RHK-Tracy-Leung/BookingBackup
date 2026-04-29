{
    'name': "BookingCustom",  # 模块的名称
    'depends': ['base', 'mail', 'sale', 'website'],
    'data': [
        'views/booking_statistics.xml',
        'views/booking_statistics_menu.xml',
        'views/sale_report_custom.xml',
        'views/sale_report_custom_menu.xml',
        'views/working_hours_report.xml',
        'views/working_hours_report_menu.xml',
        'views/is_public.xml'
    ],  # 这是在模块安装或升级时需加载数据文件的相对路径列表。这些路径相对于模块的根目录。通常，这些是XML和CSV文件，但也可以使用YAML格式的数据文件
    'models': [
        {
            'model': 'product.template',
            'custom': True,
            'inherit': 'product.template',
            'file': 'models/product_template.py',
        },
        {
            'model': 'booking.statistics',
            'custom': False,
            'file': 'models/booking_statistics.py',
        },
        {
            'model': 'sale.order',
            'custom': True,
            'inherit': 'sale.order',
            'file': 'models/sale_order.py',
        },
        {
            'model': 'sale.report.custom',
            'custom': False,
            'file': 'models/sale_report_custom.py',
        },
        {
            'model': 'working.hours.report',
            'custom': False,
            'file': 'models/working_hours_report.py',
        },
        {
            'model': 'mail.followers',
            'custom': True,
            'inherit': 'mail.followers',
            'file': 'models/mail_followers.py',
        },
        {
            'model': 'mail.mail',
            'custom': True,
            'inherit': 'mail.mail',
            'file': 'models/mail_mail.py',
        },
    ],
    'installable': True,  # 若为True（默认值），表示该模块可以进行安装。
    'application': True,  # 如果为True，模块作为应用列出。通常这用于一个功能区的中心模块。
    'auto_install': True,  # 若为True，表示这是一个*胶水*模块，在它所有的依赖模块安装后会被自动安装。
}
