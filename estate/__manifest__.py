# -*- coding: utf-8 -*-
{
    'name': "Estate",

    'summary': """
        Starting module for "Master the Odoo web framework, chapter 1: Build a Clicker game"
    """,

    'description': """
        Starting module for "Master the Odoo web framework, chapter 1: Build a Clicker game"
    """,

    'author': "Odoo",
    'website': "https://www.odoo.com/",
    'category': 'Tutorials/AwesomeClicker',
    'version': '0.1',
    'application': True,
    'installable': True,
    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
        'views/estate_property_types.xml',
        'views/estate_menus.xml',
        'views/user_views.xml',
        'views/settings_tags.xml'
    ],
    'license': 'AGPL-3'
}