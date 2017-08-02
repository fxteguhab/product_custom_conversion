from openerp.osv import osv, fields
from openerp.tools.translate import _


# ==========================================================================================================================

class product_conversion(osv.osv):
	_name = "product.conversion"
	_description = "Product Conversion"
	
	# COLUMNS ------------------------------------------------------------------------------------------------------------------
	
	_columns = {
		'product_id': fields.many2one('product.product', 'Product'),
		'product_category_id': fields.many2one('product.category', 'Product Category'),
		'qty': fields.float('Qty.'),
		'uom_id': fields.many2one('product.uom', 'UoM'),
	}