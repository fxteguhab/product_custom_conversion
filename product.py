from openerp.osv import osv, fields
from openerp.tools.translate import _

# ==========================================================================================================================

class product_category(osv.osv):
	_inherit = 'product.category'
	
# COLUMNS ------------------------------------------------------------------------------------------------------------------
	
	_columns = {
		'product_conversion_ids': fields.one2many('product.conversion', 'product_category_id', 'Product Category Conversion'),
	}

# ==========================================================================================================================

class product_template(osv.osv):
	_inherit = 'product.template'
	
# COLUMNS ------------------------------------------------------------------------------------------------------------------
	
	_columns = {
		'product_conversion_ids': fields.one2many('product.conversion', 'product_id', 'Product Conversion'),
	}

# ==========================================================================================================================

class product_uom(osv.osv):
	_inherit = 'product.uom'
	
# COLUMNS ------------------------------------------------------------------------------------------------------------------
	
	_columns = {
		'is_auto_create': fields.boolean('Auto Create From Product Custom Conversion'),
	}
	
# DEFAULTS ------------------------------------------------------------------------------------------------------------------
	
	_defaults = {
		'is_auto_create': False,
	}