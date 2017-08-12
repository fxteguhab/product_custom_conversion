from openerp.osv import osv, fields
from openerp.tools.translate import _

class sale_order(osv.osv):
	_inherit = 'sale.order'

class sale_order_line(osv.osv):
	_inherit = 'sale.order.line'

# METHODS ---------------------------------------------------------------------------------------------------------------
	
	def _calculate_nett_price(self, cr, uid, base_price, uom_qty, qty):
		if uom_qty == 0: uom_qty = 1
		nett_price = base_price / uom_qty * qty
		return nett_price
	
	def _calculate_uom_qty(self, cr, uid, product_id, product_uom_id, product_qty):
		product_uom_obj = self.pool.get('product.uom')
		product_obj = self.pool.get('product.product')
		product = product_obj.browse(cr, uid, product_id)
		return product_uom_obj._compute_qty(cr, uid, product_uom_id, product_qty, product.product_tmpl_id.uom_po_id.id)

# OVERRIDES ---------------------------------------------------------------------------------------------------------------

	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
			lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
		result = super(sale_order_line, self).product_id_change(
			cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
			lang, update_tax, date_order, packaging, fiscal_position, flag, context=None)
		product_obj = self.pool.get('product.product')
		product_conversion_obj = self.pool.get('product.conversion')
		product_record = product_obj.browse(cr, uid, product)
		price_unit = product_record.list_price
		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product, uom, qty)
		nett_price = self._calculate_nett_price(cr, uid, price_unit, product, uom, qty)
		subtotal = nett_price * uom_qty
		if qty == 0 : qty = 1
		result['value'].update({
			'price_unit': product_record.list_price * uom_qty/qty,
			'price_subtotal': subtotal
		})
		return result

# ONCHANGE ---------------------------------------------------------------------------------------------------------------

	def onchange_order_line(self, cr, uid, ids, product_qty, price_unit, product_uom, product_id,context={}):
		product_conversion_obj = self.pool.get('product.conversion')
		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product_id, product_uom, product_qty)
		nett_price = self._calculate_nett_price(cr, uid, price_unit, product_id, product_uom, product_qty)
		subtotal = nett_price*uom_qty
		return {
			'value': {
				'price_subtotal': subtotal
			}
		}

	def onchange_product_uom_qty(self, cr, uid, ids, pricelist, product, qty=0,
			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
			lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, price_unit = False,context=None):
		result = super(sale_order_line, self).product_id_change_with_wh(
			cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
			lang, update_tax, date_order, packaging, fiscal_position, flag, warehouse_id, context=None)
		product_obj = self.pool.get('product.product')
		product_conversion_obj = self.pool.get('product.conversion')
		product_record = product_obj.browse(cr, uid, product)
		uom_qty = product_conversion_obj.get_conversion_qty(cr, uid, product, uom, qty)
		nett_price = self._calculate_nett_price(cr, uid, price_unit, product, uom, qty)
		subtotal = nett_price * uom_qty
		if qty == 0 : qty = 1

		result['value'].update({
			'price_unit': product_record.list_price * uom_qty/qty,
			'product_uom': uom,
			#'price_subtotal': subtotal
		})
		return result

# ===========================================================================================================================