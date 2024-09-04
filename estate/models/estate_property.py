# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta


class RecurringPlan(models.Model):
    _name = "estate.property"
    _description = "Estate Properties"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), 
                   ('south', 'South'), 
                   ('east', 'East'), 
                   ('west', 'West')],
        string="Garden Orientation"
    )
    active=fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        required=True,
        copy=False,
        default='new',
    )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")

    buyer = fields.Many2one("res.partner", string="Buyer")
    salesperson = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags', help="Classify and analyze your estate categories")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer(
        string="Total Area (sqm)", 
        compute="_total_area"
    )

    # Nuevo campo calculado para el mejor precio de las ofertas
    best_price = fields.Float(
        string="Best Offer Price", 
        compute="_best_price", 
        readonly=True
    )

    # Adding the Many2one field for property type
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")

    _sql_constraints = [
        ('check_positive_expected_price', 'CHECK(expected_price > 0)', 
         'The expected price must be strictly positive.'),
        ('check_positive_selling_price', 'CHECK(selling_price >= 0)', 
         'The selling price must be positive.'),
        ('unique_property_name', 'UNIQUE(name)', 
         'The property name must be unique.')
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if record.expected_price > 0:
                if record.selling_price and record.selling_price < 0.9 * record.expected_price:
                    raise ValidationError("The selling price cannot be lower than 90% of the expected price.")

    @api.depends('living_area', 'garden_area')
    def _total_area(self):
        for record in self:
            # Si garden_area es None, se considera como 0 en la suma
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends('offer_ids.price')
    def _best_price(self):
        for record in self:
            # Calcula el precio máximo de las ofertas
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0

    # Métodos para los botones
    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("A canceled property cannot be set as sold.")
            record.state = 'sold'

    def action_set_canceled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be canceled.")
            record.state = 'cancelled'

    @api.ondelete(at_uninstall=False)
    def _check_ondelete(self):
        # This method will be called when a record is about to be deleted
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise ValidationError("You cannot delete properties that are not 'New' or 'Canceled'.")
