from openerp.osv import osv, fields
from openerp.tools.translate import _

_APPLIED_TO = [
	('product', 'Product'),
	('category', 'Product Category'),
]


# ==========================================================================================================================

class product_conversion(osv.osv):
	_name = "product.conversion"
	_description = "Product Conversion"
	
# COLUMNS ------------------------------------------------------------------------------------------------------------------
	
	_columns = {
		'product_id': fields.many2one('product.template', 'Product', ondelete='cascade'),
		'product_category_id': fields.many2one('product.category', 'Product Category', ondelete='cascade'),
		'conversion': fields.float('Qty.', required=True),
		'uom_id': fields.many2one('product.uom', 'UoM', required=True, ondelete='cascade'),
		'applied_to' :fields.selection(_APPLIED_TO, 'Applied To', required=True,
			help='Whether this conversion is for product or product category'),
	}
	
# DEFAULTS ------------------------------------------------------------------------------------------------------------------
	
	_defaults = {
		'applied_to': 'product',
	}
	
# CONSTRAINTS ---------------------------------------------------------------------------------------------------------------
	
	def _check_applied_to_product(self, cr, uid, ids, context=None):
		for conversion in self.browse(cr, uid, ids, context):
			if conversion.applied_to == 'product' and not conversion.product_id:
				return False
		return True
	
	def _check_applied_to_product_category(self, cr, uid, ids, context=None):
		for conversion in self.browse(cr, uid, ids, context):
			if conversion.applied_to == 'category' and not conversion.product_category_id:
				return False
		return True
	
	_constraints = [
		(_check_applied_to_product, _('You must input field product if you applied to product'), ['applied_to', 'product_id']),
		(_check_applied_to_product_category, _('You must input field product category if you applied to product category'), ['applied_to', 'product_category_id']),
	]
	
	_sql_constraints = [
		('unique_product_conversion', 'UNIQUE(product_id,uom_id)', _('You cannot assign the same conversion UOM more than once under one product.')),
		('unique_product_category_conversion', 'UNIQUE(product_category_id,uom_id)', _('You cannot assign the same conversion UOM more than once under one product category.')),
	]