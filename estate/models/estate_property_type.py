# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RecurringPlan(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Types"
    _order = "name"

    name = fields.Char(required=True)

    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")

    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
