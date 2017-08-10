from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class purchase_order(osv.osv):
	_inherit = 'purchase.order'
	
	def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
		res = super(purchase_order, self)._prepare_order_line_move(cr, uid,  order, order_line, picking_id, group_id, context=None)
		data_obj = self.pool.get('ir.model.data')
		product_conversion_obj = self.pool.get('product.conversion')
		unit_id = data_obj.get_object(cr, uid, 'product', 'product_uom_unit').id
		for dict in res:
			dict['product_uom_qty'] = product_conversion_obj.get_conversion_qty(cr, uid, dict['product_id'], dict['product_uom'], dict['product_uom_qty'])
			dict['product_uom'] = unit_id
		return res

# ===========================================================================================================================

class purchase_order_line(osv.osv):
	_inherit = 'purchase.order.line'
		
# FIELD FUNCTION METHODS ------------------------------------------------------------------------------------------------
	
	# def _price_unit_nett(self, cr, uid, ids, field_name={}, arg={}, context={}):
	# 	result = {}
	# 	lines = self.browse(cr, uid, ids, context=context)
	# 	for line in lines:
	# 		result[line.id] = self._calc_line_base_price(cr, uid, line, context=context)
	# 	return result

	# def _amount_line(self, cr, uid, ids, prop, arg, context=None):
	# 	res = super(purchase_order_line, self)._amount_line(cr, uid, ids, prop, arg, context)
	# 	product_conversion_obj = self.pool.get('product.conversion')
	# 	for id, subtotal in res.iteritems():
	# 		line = self.browse(cr, uid, [id], context=context)
	# 		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, line.product_id.id, line.product_uom.id, line.product_qty)
	# 		res[id] *= (uom_qty / line.product_qty)
	# 	return res
	
# COLUMNS ---------------------------------------------------------------------------------------------------------------
	
	_columns = {
		#'price_unit_nett': fields.function(_price_unit_nett, method=True, string='Unit Price (Nett)', type='float'),
		#'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
	}
		
# CONSTRAINTS -----------------------------------------------------------------------------------------------------------
	
	def _check_uom_conversion(self, cr, uid, ids, context=None):
		purchase_order_lines = self.browse(cr, uid, ids)
		product_conversion_obj = self.pool.get('product.conversion')
		for line in purchase_order_lines:
			try:
				product_conversion_obj.get_conversion_qty(cr, uid, line.product_id.id, line.product_uom.id, line.product_qty)
			except:
				return False
		return True

	_constraints = [
		(_check_uom_conversion, _('There are products that have invalid UOM conversion.'), ['product_uom']),
	]
		
	# METHODS ---------------------------------------------------------------------------------------------------------------
					
	def _calculate_nett_price_custom_conversion(self, cr, uid, base_price, product_id, uom_id, qty):
		product_conversion_obj = self.pool.get('product.conversion')
		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product_id, uom_id, qty)
		if uom_qty == 0: uom_qty = 1
		nett_price = base_price / uom_qty * qty
		return nett_price
			
# OVERRIDES ---------------------------------------------------------------------------------------------------------------
		
	# def _calc_line_base_price(self, cr, uid, line, context=None):
	# 	base_price = super(purchase_order_line, self)._calc_line_base_price(cr, uid, line, context)
	#	product_conversion_obj = self.pool.get('product.conversion')
	# 	qty = product_conversion_obj.get_conversion_qty(cr, uid, line.product_id.id, line.uom_id.uom_id, line.product_qty)
	# 	base_price = self._calculate_nett_price(cr, uid, line.price_unit, line.product_id, line.uom_id, line.product_qty)
	# 	return base_price
		
	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
			partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
			name=False, price_unit=False, state='draft', context=None):
		result = super(purchase_order_line, self).onchange_product_id(
			cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order, fiscal_position_id,
			date_planned, name, price_unit, state, context)
		product_obj = self.pool.get('product.product')
		product_conversion_obj = self.pool.get('product.conversion')
		product = product_obj.browse(cr, uid, product_id)
		price_unit = product.standard_price
		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product_id, uom_id, qty)
		nett_price = self._calculate_nett_price_custom_conversion(cr, uid, price_unit, product_id, uom_id, qty)
		subtotal = nett_price * uom_qty
		if qty == 0 : qty = 1
		result['value'].update({
			'price_unit': product.standard_price * uom_qty/qty,
			#'price_unit_nett': nett_price,
			'price_subtotal': subtotal
		})
		return result
			
# ONCHANGE ---------------------------------------------------------------------------------------------------------------
	
	def onchange_order_line(self, cr, uid, ids, product_qty, price_unit, product_uom, product_id,context={}):
		product_conversion_obj = self.pool.get('product.conversion')
		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product_id, product_uom, product_qty)
		nett_price = self._calculate_nett_price_custom_conversion(cr, uid, price_unit, product_id, product_uom, product_qty)
		subtotal = nett_price*uom_qty
		return {
			'value': {
				#'price_unit_nett': nett_price,
				'price_subtotal': subtotal
			}
		}
		
		
# ===========================================================================================================================