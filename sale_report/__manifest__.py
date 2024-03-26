{
    "name": "User Sale analysis",
    "summary": "module to create Sale Reporting",
    'depends': ['base', 'sale', 'account'],
    'data': ['security/ir.model.access.csv',
             'views/menu.xml',
             'views/sale_report.xml',
             'report/report.xml',
             'report/sale_report_pdf.xml',
             'security/security.xml',
             'data/mail_template.xml',
             'data/cron.xml'
             ],
}
