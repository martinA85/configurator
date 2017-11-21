# -*- coding: utf-8 -*-
{
    'name': "Odoo product configurator",
    'js': ['static/js/config.js'],
    'test': ['static/js/config.js'],
    'category' : 'Website'
    'summary': """
        Allow you to add a dynamic product configurator on your website""",

    'description': """
        This module allows you to add dynamics product configurator for you'r products web page. You can allow your customer to take order of your product with their configuration or jsut ask for a quotation.
        This module his let ypu choice between two layout for you'r product : vertcal or horizontal.
    """,

    'author': "Noosys",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'test',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','product', 'website_sale', 'website', 'website_form','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/templates_front.xml',
        'data/data.xml',
    ],
    # 'application': True,
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "price":100,
    "currency":"EUR",
    "installable":True,
    "auto_install":False,
}
