from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class purchase_order_line(osv.osv):
	_inherit = 'purchase.order.line'
		
# FIELD FUNCTION METHODS ------------------------------------------------------------------------------------------------
	
	# def _price_unit_nett(self, cr, uid, ids, field_name={}, arg={}, context={}):
	# 	result = {}
	# 	lines = self.browse(cr, uid, ids, context=context)
	# 	for line in lines:
	# 		result[line.id] = self._calc_line_base_price(cr, uid, line, context=context)
	# 	return result

	def _amount_line(self, cr, uid, ids, prop, arg, context=None):
		res = super(purchase_order_line, self)._amount_line(cr, uid, ids, prop, arg, context)
		for id, subtotal in res.iteritems():
			line = self.browse(cr, uid, [id], context=context)
			uom_qty = self._get_conversion_qty(cr, uid, line.product_id.id, line.product_uom.id, line.product_qty)
			res[id] *= (uom_qty / line.product_qty)
		return res
	
	# COLUMNS ---------------------------------------------------------------------------------------------------------------
	
	_columns = {
		#'price_unit_nett': fields.function(_price_unit_nett, method=True, string='Unit Price (Nett)', type='float'),
		'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
	}
		
	# CONSTRAINTS -----------------------------------------------------------------------------------------------------------
	
	
	def _check_uom_conversion(self, cr, uid, ids, context=None):
		purchase_order_lines = self.browse(cr, uid, ids)
		for line in purchase_order_lines:
			try:
				self._get_conversion_qty(cr, uid, line.product_id, line.uom_id, line.product_qty)
			except:
				return False
		return True

	_constraints = [
		(_check_uom_conversion, _('Purcase Discount is Not Valid.'), ['purchase_discount']),
	]
		
	# METHODS ---------------------------------------------------------------------------------------------------------------
	
	def _get_conversion_qty(self, cr, uid, product_id, uom_id, qty):
		product_conversion_obj = self.pool.get('product.conversion')
		product_obj = self.pool.get('product.product')
		product_template_obj = self.pool.get('product.template')
		product_category_obj = self.pool.get('product.category')
	# Find conversion uom for product
		conversion_product_ids = product_conversion_obj.search(
			cr, uid, [('product_id','=',product_id),('uom_id','=',uom_id),('applied_to','=','product')])
		if len(conversion_product_ids) > 0:
			return product_conversion_obj.browse(cr, uid, conversion_product_ids[0]).conversion # it must be unique, i.e ids conversion_product_ids just contain 1 id
		else:
			product = product_obj.browse(cr, uid, product_id)
			product_temp = product_template_obj.browse(cr, uid, product.product_tmpl_id.id)
			product_category = product_category_obj.browse(cr, uid, product_temp.categ_id.id)
		# Find conversion uom for product category if not found in conversion uom for product
			conversion_product_ids = product_conversion_obj.search(
				cr, uid, [('product_category_id','=',product_category.id),('uom_id','=',uom_id),('applied_to','=','category')])
			if len(conversion_product_ids) > 0:
				return product_conversion_obj.browse(cr, uid, conversion_product_ids[0]).conversion # it must be unique, i.e ids conversion_product_ids just contain 1 id
			else:
				product_uom_obj = self.pool.get('product.uom')
				product_obj = self.pool.get('product.product')
				product = product_obj.browse(cr, uid, product_id)
				uom = product_uom_obj.browse(cr, uid, uom_id)
			
			# If UOM Type is reference, or factor_inv value is -1 then raise
				if uom and (uom.uom_type == 'reference' or uom.factor_inv == -1):
					raise osv.except_orm(_('Finding conversion error'), _('Product %s do not have UOM conversion for UOM %s' %(product.name, uom.name)))
			# Find conversion uom on global if not found in conversion uom for product category
				qty_global =  product_uom_obj._compute_qty(cr, uid, uom_id, qty, product.product_tmpl_id.uom_po_id.id)
				if qty_global == -1:
					raise osv.except_orm(_('Finding conversion error'), _('Product %s do not have UOM conversion for UOM %s' %(product.name, uom.name)))
				else:
					return qty_global
				
	def _calculate_nett_price(self, cr, uid, base_price, product_id, uom_id, qty):
		uom_qty = self._get_conversion_qty(cr, uid, product_id, uom_id, qty)
		if uom_qty == 0: uom_qty = 1
		nett_price = base_price / uom_qty * qty
		# TODO hitung discount dari odoo asli
		# If discount is not counted on subtotal, but on the base price, then count the discount
		return nett_price
			
# OVERRIDES ---------------------------------------------------------------------------------------------------------------
		
	def _calc_line_base_price(self, cr, uid, line, context=None):
		base_price = super(purchase_order_line, self)._calc_line_base_price(cr, uid, line, context)

		qty = self._get_conversion_qty(cr, uid, line.product_id.id, line.uom_id.uom_id, line.product_qty)
		base_price = self._calculate_nett_price(cr, uid, line.price_unit, line.product_id, line.uom_id, line.product_qty)
		return base_price
	
	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
			partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
			name=False, price_unit=False, state='draft', context=None):
		result = super(purchase_order_line, self).onchange_product_id(
			cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order, fiscal_position_id,
			date_planned, name, price_unit, state, context)
		product_obj = self.pool.get('product.product')
		product = product_obj.browse(cr, uid, product_id)

		unit_qty = self._get_conversion_qty(cr, uid, product_id, uom_id, qty)
		nett_price = self._calculate_nett_price(cr, uid, price_unit, product_id, uom_id, qty)
		subtotal = nett_price * unit_qty
		result['value'].update({
			'price_unit': product.standard_price,
			#'price_unit_nett': nett_price,
			'price_subtotal': subtotal
		})
		return result
	
	def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
			partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
			name=False, price_unit=False, state='draft', context=None):
		result = super(purchase_order_line, self).onchange_product_uom(
			cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order, fiscal_position_id,
			date_planned, name, price_unit, state, context)
		product_obj = self.pool.get('product.product')
		product = product_obj.browse(cr, uid, product_id)
		
		unit_qty = self._get_conversion_qty(cr, uid, product_id, uom_id, qty)
		nett_price = self._calculate_nett_price(cr, uid, price_unit, product_id, uom_id, qty)
		subtotal = nett_price * unit_qty
		result['value'].update({
			'price_unit': product.standard_price,
			#'price_unit_nett': nett_price,
			'price_subtotal': subtotal
		})
		return result
	
	# ONCHANGE ---------------------------------------------------------------------------------------------------------------
	
	def onchange_order_line(self, cr, uid, ids, product_qty, price_unit, product_uom, product_id,context={}):
		uom_qty = self._get_conversion_qty(cr, uid, product_id, product_uom, product_qty)
		nett_price = self._calculate_nett_price(cr, uid, price_unit, product_id, product_uom, product_qty)
		subtotal = nett_price*uom_qty
		return {
			'value': {
				#'price_unit_nett': nett_price,
				'price_subtotal': subtotal
			}
		}
		
		
		# ==========================================================================================================================