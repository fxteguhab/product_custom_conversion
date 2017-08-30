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
		'product_template_id': fields.many2one('product.template', 'Product', ondelete='cascade'),
		'product_category_id': fields.many2one('product.category', 'Product Category', ondelete='cascade'),
		'conversion': fields.float('Conversion Qty.', required=True),
		'uom_id': fields.many2one('product.uom', 'UoM', required=True, ondelete='cascade', domain=[('uom_type','!=','reference'), ('is_auto_create','=',False)]),
		'applied_to' :fields.selection(_APPLIED_TO, 'Applied To', required=True,
			help='Whether this conversion is for product or product category'),
		'uom_type': fields.selection([('bigger','Bigger than the reference Unit of Measure'),
			('reference','Reference Unit of Measure for this category'),
			('smaller','Smaller than the reference Unit of Measure')],'Type', required=1),
		'auto_uom_id': fields.many2one('product.uom', 'UoM'),
		'uom_category_filter_id': fields.many2one('product.uom.categ', 'UoM Category', ondelete='restrict'),
	}
	
# DEFAULTS ------------------------------------------------------------------------------------------------------------------
	
	_defaults = {
		'applied_to': 'product',
	}
	
# CONSTRAINTS ---------------------------------------------------------------------------------------------------------------
	
	def _check_applied_to_product(self, cr, uid, ids, context=None):
		for conversion in self.browse(cr, uid, ids, context):
			if conversion.applied_to == 'product' and not conversion.product_template_id:
				return False
		return True
	
	def _check_applied_to_product_category(self, cr, uid, ids, context=None):
		for conversion in self.browse(cr, uid, ids, context):
			if conversion.applied_to == 'category' and not conversion.product_category_id:
				return False
		return True
	
	_constraints = [
		(_check_applied_to_product, _('You must input field product if you applied to product'), ['applied_to', 'product_template_id']),
		(_check_applied_to_product_category, _('You must input field product category if you applied to product category'), ['applied_to', 'product_category_id']),
	]
	
	_sql_constraints = [
		('unique_product_conversion', 'UNIQUE(product_template_id,uom_id)', _('You cannot assign the same conversion UOM more than once under one product.')),
		('unique_product_category_conversion', 'UNIQUE(product_category_id,uom_id)', _('You cannot assign the same conversion UOM more than once under one product category.')),
	]
	
# OVERRIDE ------------------------------------------------------------------------------------------------------------------
	
	def create(self, cr, uid, data, context=None):
		product_uom_obj = self.pool.get('product.uom')
		product_uom = product_uom_obj.browse(cr, uid, data['uom_id'])
		data_product_uom = {
			'name' 			: product_uom.name +'('+ str(data['conversion']) +')',
			'category_id'	: product_uom.category_id.id,
			'uom_type'		: data['uom_type'],
			'rounding'		: product_uom.rounding,
			'active'		: True,
			'is_auto_create': True,
			'factor'		: data['conversion'],
		}
		if data['uom_type'] == 'bigger':
			data_product_uom['factor_inv'] = data['conversion']
		
		auto_uom_id =  product_uom_obj.create(cr, uid, data_product_uom, context)
		data['auto_uom_id'] = auto_uom_id
		
		return super(product_conversion, self).create(cr, uid, data, context)
	
	def write(self, cr, uid, ids, vals, context={}):
		product_uom_obj = self.pool.get('product.uom')
		res = super(product_conversion, self).write(cr, uid, ids, vals, context=context)
		for record in self.browse(cr, uid, ids):
			product_uom = product_uom_obj.browse(cr, uid, record.uom_id.id)
			if vals.get('conversion', False):
				product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'name' : product_uom.name +'('+ str(vals['conversion']) +')'}, context)
				if vals.get('uom_type', False) == 'bigger':
					product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'factor_inv' : vals['conversion']}, context)
				else:
					if record.uom_type == 'bigger':
						product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'factor_inv' : vals['conversion']}, context)
					else:
						product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'factor' : vals['conversion']}, context)
					
			if vals.get('uom_id', False):
				try:
					product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'category_id' : product_uom.category_id.id}, context)
				except:
					raise osv.except_osv(_('Error'), _('Cannot change to %s, it has different UOM categories') % product_uom.name)
				product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'name' : product_uom.name +'('+ str(record.conversion) +')'}, context)
			if vals.get('uom_type', False):
				if vals.get('uom_type', False) == 'bigger':
					if vals.get('conversion', False):
						product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'factor_inv' : vals['conversion']}, context)
					else:
						product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'factor_inv' : record.conversion}, context)
				product_uom_obj.write(cr, uid, [record.auto_uom_id.id],{'uom_type' : vals['uom_type']}, context)
				
		return res
	
	def unlink(self, cr, uid, ids, context={}):
		product_uom_obj = self.pool.get('product.uom')
		for record in self.browse(cr, uid, ids):
			product_uom_obj.unlink(cr, uid, [record.auto_uom_id.id], context)
		return super(product_conversion, self).unlink(cr, uid, ids, context=context)
	
# METHOD --------------------------------------------------------------------------------------------------------------------
	
	def get_conversion_auto_uom(self, cr, uid, product_id, uom_id):
		product_obj = self.pool.get('product.product')
		product_template_obj = self.pool.get('product.template')
		product_category_obj = self.pool.get('product.category')
		product_uom_obj = self.pool.get('product.uom')
		product = product_obj.browse(cr, uid, product_id)
		product_temp = product_template_obj.browse(cr, uid, product.product_tmpl_id.id)
		# Find conversion uom for product
		conversion_product_ids = self.search(
			cr, uid, [('product_template_id','=',product_temp.id),('uom_id','=',uom_id),('applied_to','=','product')])
		if len(conversion_product_ids) > 0:
			record_conversion = self.browse(cr, uid, conversion_product_ids[0]) # it must be unique, i.e ids conversion_product_ids just contain 1 id
			return product_uom_obj.browse(cr, uid, record_conversion.auto_uom_id.id)
		else:
			product_category = product_category_obj.browse(cr, uid, product_temp.categ_id.id)
			# Find conversion uom for product category if not found in conversion uom for product
			conversion_product_ids = self.search(
				cr, uid, [('product_category_id','=',product_category.id),('uom_id','=',uom_id),('applied_to','=','category')])
			if len(conversion_product_ids) > 0:
				record_conversion = self.browse(cr, uid, conversion_product_ids[0]) # it must be unique, i.e ids conversion_product_ids just contain 1 id
				return product_uom_obj.browse(cr, uid, record_conversion.auto_uom_id.id)
			else:
				uom = product_uom_obj.browse(cr, uid, uom_id)
				return uom
				
	def onchange_product_uom(self, cr, uid, ids, product_uom_id):
		product_uom_obj = self.pool.get('product.uom')
		product_uom = product_uom_obj.browse(cr, uid, product_uom_id)
		return {
			'value': {
				'uom_type': product_uom.uom_type
			}
		}
	
	def get_uom_from_auto_uom(self, cr, uid, auto_uom_id, context):
		conversion_ids = self.search(cr, uid, [('auto_uom_id','=', auto_uom_id)])
		product_uom_obj = self.pool.get('product.uom')
		if len(conversion_ids) > 0:
			conversion = self.browse(cr, uid, conversion_ids[0])
			return product_uom_obj.browse(cr, uid, conversion.uom_id.id)
		else:
			return product_uom_obj.browse(cr, uid, auto_uom_id)
	
	def onchange_product_application(self, cr, uid, ids, applied_to, product_category_id, product_template_id):
		if applied_to and applied_to == 'product' and product_template_id:
			product_template_obj = self.pool.get('product.template')
			product_template = product_template_obj.browse(cr, uid, product_template_id)
			return {
				'value': {
					'uom_category_filter_id': product_template.uom_id.category_id.id,
				}
			}
		elif applied_to and applied_to == 'category' and product_category_id:
			product_category_obj = self.pool.get('product.category')
			product_category = product_category_obj.browse(cr, uid, product_category_id)
			return {
				'value': {
					'uom_category_filter_id': product_category.default_uom_id.category_id.id,
				}
			}