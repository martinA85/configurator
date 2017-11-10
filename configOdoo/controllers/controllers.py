# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class ConfigurateurProduct(http.Controller):
    

    @http.route(['/shop/config/recap'], type='http', auth="public", website=True)
    def recap_config(self, variant_lst, product_id, banquette, rideaux, dossier):
    
        print banquette
    	variant_id = variant_lst.split(',')
    	# var env is environement variable that we use to browse our object
    	env = request.env
    	# creating an empty product.template object
    	product_template = env['product.template']
    	# product is the product.template
    	product = product_template.browse(int(product_id))

    	# variant_template is a variant_product line
    	variant_template = env['configurateur_product.line']

        config = env['configurateur.config']

        config_price = product.list_price
    	# selected variant list
    	selected_variant = list()
        for id_variant in variant_id:
            try:
                variant = variant_template.browse(int(id_variant))
                selected_variant.append(variant)
            except:
                pass
        if banquette ==0:
            banquette = "default"
        else:
            banquette = variant_template.browse(int(banquette))
        if rideaux == 0:
            rideaux = "default"
        else:
            rideaux = variant_template.browse(int(rideaux))
        if dossier == 0:
            dossier = "default"
        else:
            dossier = variant_template.browse(int(dossier))
        
        values = {

            'variants':selected_variant,
            'product':product,
            'banquette':banquette,
            'rideaux':rideaux,
            'dossier':dossier
        }
        return request.render("configOdoo.recap_config",values)
        
        
    @http.route(['/shop/config/valid_request'], type='http', auth="public", website=True)
    def valid_request(self, contact_name, phone, email_form, description, refrid=0, refbanq=0, refdoss=0, ldoss=0, lrid=0, lbanq=0, Ldoss=0, Lrid=0, Lbanq=0, erid=0, ebanq=0, edoss=0):
        
        print(email_form)
        description = "Demande de devis depuis de site web (dimenssion en cm) : \n"
        description += "Banquette : "+ refbanq + " : Longueur : "+ lbanq + " - Largeur : " + Lbanq + " - Epaisseur : " + ebanq + " \n"
        description += "Dossier : "+ refdoss + " : Longueur : "+ ldoss + " - Largeur : " + Ldoss + " - Epaisseur : " + edoss + " \n"
        description += "Rideaux : "+ refrid + " : Longueur : "+ lrid + " - Largeur : " + Lrid + " - Epaisseur : " + erid + " \n"
        name = "Demande devis site web : "+contact_name
        
        vals = {
            "name" : name,
            "contact_name" : contact_name,
            "phone" : phone,
            "email_from": email_form,
            "description" : description
        }
        
        request.env['crm.lead'].create(vals)
        
        return request.render("configOdoo.thanks_page")