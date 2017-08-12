# from openerp.osv import osv, fields
# from openerp.tools.translate import _
#
# class sale_order(osv.osv):
# 	_inherit = 'sale.order'
#
# # OVERRIDES -----------------------------------------------------------------------------------------------------------------
#
# 	def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
# 		res = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id, context)
# 		data_obj = self.pool.get('ir.model.data')
# 		product_conversion_obj = self.pool.get('product.conversion')
# 		unit_id = data_obj.get_object(cr, uid, 'product', 'product_uom_unit').id
# 		qty_uom = product_conversion_obj.get_conversion_qty(cr, uid, res['product_id'], res['product_uom'], res['product_qty'])
# 		res['product_qty'] = qty_uom
# 		res['product_uos_qty'] = qty_uom
# 		res['product_uom'] = unit_id
# 		res['product_uos'] = unit_id
# 		return res
#
#
#
# # ===========================================================================================================================
#
# class sale_order_line(osv.osv):
# 	_inherit = 'sale.order.line'
#
# # CONSTRAINTS -----------------------------------------------------------------------------------------------------------
#
# 	def _check_uom_conversion(self, cr, uid, ids, context=None):
# 		sales_order_lines = self.browse(cr, uid, ids)
# 		product_conversion_obj = self.pool.get('product.conversion')
# 		for line in sales_order_lines:
# 			try:
# 				product_conversion_obj.get_conversion_qty(cr, uid, line.product_id.id, line.product_uom.id, line.product_uom_qty)
# 			except:
# 				return False
# 		return True
#
# 	_constraints = [
# 		(_check_uom_conversion, _('There are products that have invalid UOM conversion.'), ['product_uom']),
# 	]
#
# # METHODS ---------------------------------------------------------------------------------------------------------------
#
# 	def _calculate_nett_price(self, cr, uid, base_price, product_id, uom_id, qty):
# 		product_conversion_obj = self.pool.get('product.conversion')
# 		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product_id, uom_id, qty)
# 		if uom_qty == 0: uom_qty = 1
# 		nett_price = base_price / uom_qty * qty
# 		return nett_price
#
# # OVERRIDES ---------------------------------------------------------------------------------------------------------------
#
#
# 	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
# 			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
# 			lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
# 		result = super(sale_order_line, self).product_id_change(
# 			cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
# 			lang, update_tax, date_order, packaging, fiscal_position, flag, context=None)
# 		product_obj = self.pool.get('product.product')
# 		product_conversion_obj = self.pool.get('product.conversion')
# 		product_record = product_obj.browse(cr, uid, product)
# 		price_unit = product_record.list_price
# 		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product, uom, qty)
# 		nett_price = self._calculate_nett_price(cr, uid, price_unit, product, uom, qty)
# 		subtotal = nett_price * uom_qty
# 		if qty == 0 : qty = 1
# 		result['value'].update({
# 			'price_unit': product_record.list_price * uom_qty/qty,
# 			'price_subtotal': subtotal
# 		})
# 		return result
#
# # ONCHANGE ---------------------------------------------------------------------------------------------------------------
#
# 	def onchange_order_line(self, cr, uid, ids, product_qty, price_unit, product_uom, product_id,context={}):
# 		product_conversion_obj = self.pool.get('product.conversion')
# 		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product_id, product_uom, product_qty)
# 		nett_price = self._calculate_nett_price(cr, uid, price_unit, product_id, product_uom, product_qty)
# 		subtotal = nett_price*uom_qty
# 		return {
# 			'value': {
# 				'price_subtotal': subtotal
# 			}
# 		}
#
# 	def onchange_product_uom_qty(self, cr, uid, ids, pricelist, product, qty=0,
# 			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
# 			lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, price_unit = False,context=None):
# 		result = super(sale_order_line, self).product_id_change_with_wh(
# 			cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
# 			lang, update_tax, date_order, packaging, fiscal_position, flag, warehouse_id, context=None)
# 		product_obj = self.pool.get('product.product')
# 		product_conversion_obj = self.pool.get('product.conversion')
# 		product_record = product_obj.browse(cr, uid, product)
# 		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product, uom, qty)
# 		nett_price = self._calculate_nett_price(cr, uid, price_unit, product, uom, qty)
# 		subtotal = nett_price * uom_qty
# 		if qty == 0 : qty = 1
#
# 		result['value'].update({
# 			'price_unit': product_record.list_price * uom_qty/qty,
# 			'product_uom': uom,
# 			'price_subtotal': subtotal
# 		})
# 		return result
#
# # ===========================================================================================================================