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
	
# OVERRIDE ------------------------------------------------------------------------------------------------------------------

	def unlink(self, cr, uid, ids, context={}):
		conversion_obj = self.pool.get('product.conversion')
		for record in self.browse(cr, uid, ids):
			ids_conversion = conversion_obj.search(cr, uid, {'auto_uom_id' : record.id}, context)
			if len(ids_conversion) > 0:
				raise osv.except_osv(_('Delete UOM ERROR'),_('There are record on product custom conversion that reference on UOM %s') % record.name)
		return super(product_uom, self).unlink(cr, uid, ids, context=context)