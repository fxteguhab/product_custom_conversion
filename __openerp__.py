# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
	'name': "Product Custom Conversion",
	'summary': """
		Product Custom Conversion
	""",
	'description': """
		Product Custom Conversion
	""",
	'author': 'Christyan Juniady and Associates',
	'maintainer': 'Christyan Juniady and Associates',
	'website': 'http://www.chjs.biz',
	'category': 'Uncategorized',
	'version': '0.1',
	'depends': ["base","product","stock", "sale", "purchase", "sale_stock"],
	'data': [
		'views/conversion_view.xml',
		'menu/conversion_menu.xml',
		'views/product_category_view.xml',
		'views/product_view.xml',
		'views/purchase_view.xml',
		'views/sale_view.xml',
	],
	'demo': [
	],
	'installable': True,
	'auto_install': True,
}
