{
    'name': 'Ecuadorian Localization Base Customization',
    'version': '3.9',
    'summary': 'Base customization module for Ecuadorian localization',
    'description': """
    Este módulo es la personalización base para la localización ecuatoriana.
    """,
    'icon': '/account/static/description/l10n.png',
    'countries': ['ec'],
    'author': 'Elmer Salazar Arias',
    'category': 'Accounting/Localizations/Account Charts',
    'maintainer': 'Elmer Salazar Arias',
    'website': 'http://www.galapagos.tech',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'base_iban',
        'account_debit_note',
        'l10n_latam_invoice_document',
        'l10n_latam_base',
        'account',
        'l10n_ec',
        'l10n_ec_edi',
        'l10n_ec_reports',
        'l10n_ec_reports_ats',
    ],
    'data': [
        'security/security.xml',
        'views/partner_view.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'maintainer': 'Elmer Salazar Arias',
    'email': 'esalazargps@gmail.com',
}