# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RecurringPlan(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tags"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer('Color')
    
    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 
         'The property tag name must be unique.')
    ]
