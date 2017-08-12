from openerp.osv import osv, fields
from openerp.tools.translate import _

class stock_move(osv.osv):
	_inherit = 'stock.move'
	
# COLUMNS ---------------------------------------------------------------------------------------------------------------

	_columns = {
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, domain=[('is_auto_create','=',False)]),
	}

# ONCHANGE ---------------------------------------------------------------------------------------------------------------

	def onchange_product_uom(self, cr, uid, ids, product, uom=False, context= {}):
		product_conversion_obj = self.pool.get('product.conversion')
		uom_record = product_conversion_obj.get_conversion_auto_uom(cr, uid, product, uom)
		result = {'value': {
			'product_uom': uom_record.id,
		}}
		return result
		
# ===========================================================================================================================