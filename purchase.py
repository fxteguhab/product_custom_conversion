from openerp.osv import osv, fields


class purchase_order_line(osv.osv):
	_inherit = 'purchase.order.line'
		
# COLUMNS ---------------------------------------------------------------------------------------------------------------
	
	_columns = {
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
	}
				
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
	
	def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
			partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
			name=False, price_unit=False, state='draft', context=None):
		product_conversion_obj = self.pool.get('product.conversion')
		uom = product_conversion_obj.get_conversion_auto_uom(cr, uid, product_id, uom_id)
		result = super(purchase_order_line, self).onchange_product_id(
			cr, uid, ids, pricelist_id, product_id, qty, uom.id, partner_id, date_order, fiscal_position_id,
			date_planned, name, price_unit, state, context)
		uom_qty = self._calculate_uom_qty(cr, uid, product_id, uom.id, qty)
		product_obj = self.pool.get('product.product')
		product = product_obj.browse(cr, uid, product_id)
		result['value'].update({
			'product_uom': uom.id,
			'price_unit': product.standard_price * uom_qty/qty,
		})
		
		result = self._update_uom_domain(result)
		return result
	
	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order=False,
			fiscal_position_id=False, date_planned=False, name=False, price_unit=False, state='draft', context=None):
		res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
			partner_id, date_order, fiscal_position_id, date_planned, name, price_unit, state, context)
		res = self._update_uom_domain(res)
		return res
	
	def _update_uom_domain(self, onchange_result):
		if onchange_result.get('domain', False):
			if onchange_result['domain'].get('product_uom', False):
				onchange_result['domain']['product_uom'].append(('is_auto_create', '=', False))
			else:
				onchange_result['domain']['product_uom'] = [('is_auto_create', '=', False)]
		else:
			onchange_result.update({'domain': {'product_uom': [('is_auto_create', '=', False)]}})
		return onchange_result
			
# ONCHANGE ---------------------------------------------------------------------------------------------------------------
	
	def onchange_order_line(self, cr, uid, ids, product_qty, price_unit, product_uom, product_id,context={}):
		uom_qty = self._calculate_uom_qty(cr, uid, product_id, product_uom, product_qty)
		nett_price = self._calculate_nett_price(cr, uid, price_unit, uom_qty, product_qty)
		subtotal = nett_price*uom_qty
		return {
			'value': {
				'price_subtotal': subtotal
			}
		}
		
		
# ===========================================================================================================================