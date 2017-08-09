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
		'conversion': fields.float('Conversion Qty.', required=True),
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
	
# METHOD --------------------------------------------------------------------------------------------------------------------
	
	def get_conversion_qty(self, cr, uid, product_id, uom_id, qty):
		product_obj = self.pool.get('product.product')
		product_template_obj = self.pool.get('product.template')
		product_category_obj = self.pool.get('product.category')
		# Find conversion uom for product
		conversion_product_ids = self.search(
			cr, uid, [('product_id','=',product_id),('uom_id','=',uom_id),('applied_to','=','product')])
		if len(conversion_product_ids) > 0:
			return self.browse(cr, uid, conversion_product_ids[0]).conversion # it must be unique, i.e ids conversion_product_ids just contain 1 id
		else:
			product = product_obj.browse(cr, uid, product_id)
			product_temp = product_template_obj.browse(cr, uid, product.product_tmpl_id.id)
			product_category = product_category_obj.browse(cr, uid, product_temp.categ_id.id)
			# Find conversion uom for product category if not found in conversion uom for product
			conversion_product_ids = self.search(
				cr, uid, [('product_category_id','=',product_category.id),('uom_id','=',uom_id),('applied_to','=','category')])
			if len(conversion_product_ids) > 0:
				return self.browse(cr, uid, conversion_product_ids[0]).conversion # it must be unique, i.e ids conversion_product_ids just contain 1 id
			else:
				product_uom_obj = self.pool.get('product.uom')
				product_obj = self.pool.get('product.product')
				product = product_obj.browse(cr, uid, product_id)
				uom = product_uom_obj.browse(cr, uid, uom_id)
				
				# If UOM Type is reference, or factor_inv value is -1 then raise
				if product_id and (uom.factor_inv or uom.factor) == -1:
					raise osv.except_orm(_('Finding conversion error'), _('Product %s do not have UOM conversion for UOM %s' %(product.name, uom.name)))
				# Find conversion uom on global if not found in conversion uom for product category
				qty_global =  product_uom_obj._compute_qty(cr, uid, uom_id, qty, product.product_tmpl_id.uom_po_id.id)
				if qty_global == -1:
					raise osv.except_orm(_('Finding conversion error'), _('Product %s do not have UOM conversion for UOM %s' %(product.name, uom.name)))
				else:
					return qty_global