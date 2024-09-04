from odoo import models, fields

class EstateUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        'estate.property',
        'salesperson',  # This is the inverse field in estate.property
        string='Properties',
        domain="[('state', '=', 'available')]"  # Filter to only show available properties
    )