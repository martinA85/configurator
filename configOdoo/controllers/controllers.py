# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from PIL import Image
import io
from io import BytesIO
import base64
from odoo.addons.website_sale.controllers.main import WebsiteSale

class ConfigurateurProduct(http.Controller):


    @http.route(['/shop/config/recap'], type='http', auth="public", website=True)
    def recap_config(self, variant_lst, product_id, salable):

    	variant_id = variant_lst.split(',')
    	# var env is environement variable that we use to browse our object
    	env = request.env
    	# creating an empty product.template object
    	product_template = env['product.template']
    	# product is the product.template
    	product = product_template.browse(int(product_id))

        product_tmpl = env['product.product']
    	# variant_template is a variant_product line
    	variant_template = env['configurateur_product.line']
        config = env['configurateur.config']

        config_image = Image.open(BytesIO(base64.b64decode(product.background)))

        config_string = ""
        config_price = product.list_price
    	# selected variant list
    	selected_variant = list()
        config_var_ids = list()
        for id_variant in variant_id:
            try:
                variant = variant_template.browse(int(id_variant))
                selected_variant.append(variant)
                config_var_ids.append(variant.id)
                config_price += variant.extra_price
                var_img = Image.open(BytesIO(base64.b64decode(variant.image))).convert("RGBA")
                var_img.convert('RGB')
                config_image.paste(var_img, (0,0),var_img)
            except:
                pass

        #generating configured product image using io library
        in_nem_file = io.BytesIO()
        config_image.save(in_nem_file, format="png")
        in_nem_file.seek(0)
        config_image = base64_encoded_result_bytes = base64.b64encode(in_nem_file.read())

        #creating the config object
        vals = {
            'total_price':str(config_price),
            'variant_line_ids':[(6,0,config_var_ids)],
            'config_image' : config_image
        }

        config = config.create(vals)

        #creating base product.product if not exist
        prod_base = product_tmpl.search([['default_code','=', 'conf_base'],['product_tmpl_id','=',int(product_id)]])
        if not prod_base:
            vals = {
                'product_tmpl_id' : product.id,
                'image_variant' : product.image,
                'default_code' : 'conf_base',
            }
            prod_base = product_tmpl.create(vals)

        #creating configured product.product if not exist
        prod_config = product_tmpl.search([['default_code','=', config.config_code],['product_tmpl_id','=',int(product_id)]])
        if not prod_config:
            vals = {
                'product_tmpl_id' : product.id,
                'image_variant' : config.config_image,
                'config_id' : config.id,
                'default_code' : config.config_code,
            }
            prod_config = product_tmpl.create(vals)

        #value to return to the view
        values = {
            'variants':selected_variant,
            'product':product,
            'config':config,
            'salable':salable,
            'product_config':prod_config
        }
        #returning the view
        return request.render("configOdoo.recap_config",values)


class SaleSite(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id ,add_qty=1, set_qty=0,config=None,**kw):
        if(config == None):
            #if product isn't a configured product, we apply original odoo treatment
            to_return = super(SaleSite, self).cart_update(product_id)
        if(config != None):
            #if product is a configured product we call our treatment
            request.website.sale_get_order(force_create=1)._cart_update(
                config=config,
                product_id=int(product_id),
                add_qty=float(add_qty),
                set_qty=float(set_qty),
                attributes=self._filter_attributes(**kw),
            )
        return request.redirect("/shop/cart")


    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        to_return = super(SaleSite, self).confirm_order(**post)
        order = request.website.sale_get_order()
        lines = order.order_line
        #used to be sure that order.line amount will be the right one
        for line in lines:
            if line.config != None:
                order.amount_total += line.extra_config
                line.price_unit += line.extra_config
        return to_return


    @http.route(['/shop/config/ask_qutoation'], type="http", auth="public", website=True,csrf=False)
    def ask_quotation(self, contact_name, phone, email_form, config_id, product_id, qty):
        product = request.env['product.product'].browse(int(product_id))
        #this will be in description of the lead
        description = "Configuration for product : " + str(product.name) + ", quantity asked : " + str(qty)
        #we are getting back config object
        config = request.env['configurateur.config'].browse(int(config_id))
        variant_line_ids = config.variant_line_ids

        name = "Quotation ask for " + product.name

        vals = {
            "name" : name,
            "contact_name" : contact_name,
            "phone" : phone,
            "email_from" : email_form,
            "description" : description,
            "variant_line_ids" : variant_line_ids,
        }

        lead  = request.env['crm.lead'].create(vals)
        #we are adding variant_line link after creating, doesnt work during the creation
        lead.variant_line_ids = variant_line_ids
        #return of the view
        return request.render("configOdoo.thanks_page")
