from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta

class EstateOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offers"
    _order = "price desc"

    # Fields
    price = fields.Float(string="Price", required=True)
    
    # Selection field with possible values "Accepted" and "Refused"
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused')],
        string="Status",
        copy=False  # No copy indicates the field should not be copied when duplicating records
    )
    
    # Many2one relationship to res.partner (Partner)
    partner_id = fields.Many2one(
        'res.partner', 
        string="Partner", 
        required=True
    )
    
    # Many2one relationship to estate.property (Property)
    property_id = fields.Many2one(
        'estate.property', 
        string="Property", 
        required=True
    )

    # Nuevo campo de validez con valor por defecto de 7 días
    validity = fields.Integer(string="Validity (days)", default=7)

    # Nuevo campo calculado de fecha límite
    date_deadline = fields.Date(
        string="Deadline", 
        compute="_date_deadline", 
        inverse="_inverse_date_deadline"
    )

    _sql_constraints = [
        ('check_positive_offer_price', 'CHECK(price > 0)', 
         'The offer price must be strictly positive.')
    ]

    @api.depends('create_date', 'validity')
    def _date_deadline(self):
        for offer in self:
            if offer.create_date:
                # Calcula la fecha límite como la fecha de creación más la validez en días
                offer.date_deadline = offer.create_date + timedelta(days=offer.validity)
            else:
                # Fallback para cuando create_date aún no esté establecido
                offer.date_deadline = fields.Date.today() + timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date:
                # Calcula la validez como la diferencia en días entre la fecha de creación y la fecha límite
                offer.validity = (offer.date_deadline - offer.create_date.date()).days
            else:
                # Fallback para cuando create_date aún no esté establecido
                offer.validity = (offer.date_deadline - fields.Date.today()).days

    # Métodos para los botones
    def action_accept(self):
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("Cannot accept an offer for a sold property.")
            offer.status = 'accepted'
            # Actualizar precio de venta de la propiedad
            offer.property_id.selling_price = offer.price
            # Cambiar estado de la propiedad si es necesario
            offer.property_id.state = 'offer_received'
            # Agregar al socio como comprador
            offer.property_id.buyer = offer.partner_id

    def action_refuse(self):
        for offer in self:
            offer.status = 'refused'

    @api.model
    def create(self, vals):
        # Get the property ID from the vals
        property_id = vals.get('property_id')
        
        # Instantiate the estate.property model
        estate_property = self.env['estate.property'].browse(property_id)
        
        # Check if there are existing offers
        existing_offers = self.search([('property_id', '=', property_id)])
        
        # If the offer price is lower than any existing offer, raise an error
        new_offer_price = vals.get('price', 0)
        if any(existing_offer.price >= new_offer_price for existing_offer in existing_offers):
            raise ValidationError("The offer price must be higher than existing offers.")
        
        # Call the super method to create the offer
        offer = super(EstateOffer, self).create(vals)
        
        # Update the property state to "Offer Received"
        if property_id:
            estate_property.write({'state': 'offer_received'})
        
        return offer
