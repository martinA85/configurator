# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

# Herite du model produit pour rajouter un champ configurable
class Product(models.Model):
	_inherit = 'product.template'

	is_configurable = fields.Boolean(string="Configurable", index=True, default=False)
	variant_ids = fields.Many2many('configurateur_product.variant', string="Variants")
	background = fields.Binary("Image", attachment=True, help="770px max width for horizontal layout, 570 px max width for vertical layout")
	layout = fields.Selection([('v','Vertical'),('h','Horizontal')])
	is_composer = fields.Boolean(string="composée", default=False, help="Yes if the product can be a part of a configured product")
	config_salable = fields.Boolean(string="Salable", default=False, help="If the product is salable, customer will be able to add the product to cart, if the product is not salable, customer will be able to ask for a quotation")


class ProductProduct(models.Model):
	_inherit = "product.product"

	config_id = fields.Many2one("configurateur.config", readonly="1")

	def _compute_product_price(self):
		super(ProductProduct,self)._compute_product_price()
		for record in self:
			if record.config_id:
				record.price = record.config_id.total_price

class Variant(models.Model):
	_name="configurateur_product.variant"

	name = fields.Char(string = "Variant name", help="This name should be unique")
	libelle = fields.Char(string = "Name printed on the website")
	material_ids = fields.One2many('configurateur.material', 'variant_id',string="material")


class Line_variant(models.Model):
	_name="configurateur_product.line"
	_rec_name = 'name'

	name = fields.Char(string="Variant line reference", help="Should be unique")
	libelle = fields.Char(string = "Name printed on the website")
	image = fields.Binary("Image", attachment=True, help="770px max width for horizontal layout, 570 px max width for vertical layout")
	icon = fields.Binary("Image", attachment=True, help="This field holds the image used as image for the product, limited to 1024x1024px.")
	extra_price = fields.Float("Extra price", default=0)
	material_id = fields.Many2one('configurateur.material','line_ids', visible="0")
	variant_string = fields.Char(compute="_compute_variant_string")

	@api.depends('material_id')
	def _compute_variant_string(self):
		for record in self:
			record.variant_string = record.material_id.variant_id.libelle


class variant_material(models.Model):
	_name="configurateur.material"

	name = fields.Char()
	libelle = fields.Char(string = "Name printed on the website")
	line_ids = fields.One2many('configurateur_product.line', 'material_id',string="Variant line list")
	href_id = fields.Char(compute="_compute_href", readonly="1", visible="0")
	variant_id = fields.Many2one('configurateur_product.variant',visible="0")

	def _compute_href(self):
		for record in self:
			record.href_id = "#"+str(record.id)

class ConfigProduct(models.Model):
	_name="configurateur.config"

	total_price = fields.Float("Total Cost", default=0)
	variant_line_ids = fields.Many2many("configurateur_product.line", string="Variant line list")
	config_image = fields.Binary("Image", attachment=True)
	config_code = fields.Char(readonly="1", visible="0", compute="_compute_config_code")

	def _compute_config_code(self):
		for record in self:
			if not record.variant_line_ids:
				record.config_code = "conf_base"
			else:
				record.config_code = "conf"
				for variant in record.variant_line_ids:
					record.config_code = record.config_code + "_" + variant.name

class SaleOrderLine(models.Model):
	_inherit="sale.order.line"

	extra_config = fields.Monetary(string="extra config price")
	config = fields.Many2one("configurateur.config", readonly="1", visible="0")
	variant_line_ids = fields.Many2many("configurateur_product.line")
	config_txt = fields.Char(compute="_compute_code_config")

	@api.depends('config')
	def _compute_code_config(self):
		for record in self:
			record.config_txt = ""
			for line in record.config.variant_line_ids:
				record.config_txt = record.config_txt + str(line.variant_string) + " : " + str(line.name) + "\n"


	@api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
	def _compute_amount(self):
		#this function is herited to update price while using js_add_cart_json button on cart view
		to_return = super(SaleOrderLine,self)._compute_amount()
		for line in self:
			if(line.config.total_price == 0):
				price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
			else :
				price = line.config.total_price * (1 - (line.discount or 0.0) / 100.0)
			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
			line.update({
			'price_tax': taxes['total_included'] - taxes['total_excluded'],
				'price_total': taxes['total_included'],
				'price_subtotal': taxes['total_excluded'],
			})


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, attributes=None,config=None,**kwargs):
    	to_return = super(SaleOrder, self)._cart_update(product_id=int(product_id),add_qty=add_qty, set_qty=set_qty)
    	order_line = self._cart_find_product_line(product_id, line_id, **kwargs)
    	product = self.env['product.product'].browse(product_id)
		#if product is a configured product
    	if config != None:
    		config_tmp = self.env['configurateur.config']
    		config = config_tmp.browse(int(config))

    		price = config.total_price
    		order_line.config = config.id
    		order_line.variant_line_ids = config.variant_line_ids
    		order_line.total_price = price
    		order_line.extra_config = price - product.price
			#recomputing order.line price
    		order_line._compute_amount()
    		values = self._website_product_id_change(self.id, product_id, qty=order_line.product_uom_qty)
			#recomputing taxes
    		values['price_unit'] = self.env['account.tax']._fix_tax_included_price(
                    order_line._get_display_price(product),
                    order_line.product_id.taxes_id,
                    order_line.tax_id
    		)
			#updating order line
    		order_line.write(values)
    		return {"line_id":order_line.id, 'quantity':1}
    	else:
    		return to_return


class Lead(models.Model):
	_inherit = "crm.lead"

	variant_line_ids = fields.Many2many("configurateur_product.line")


class SaleConfigSetting(models.TransientModel):
	_inherit = "sale.config.settings"

	@api.model
	def activate_product_variant(self):
		self.update({'group_product_variant':True})
