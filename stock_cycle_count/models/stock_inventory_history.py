# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockInventoryHistory(models.Model):
    _name = 'stock.inventory.history'
    _description = 'History of inventory accuracies'
    _rec_name = 'location_id'

    location_id = fields.Many2one(comodel_name='stock.location',
                                  string='Location')
    inventory_id = fields.Many2one(comodel_name='stock.inventory',
                                   string='Inventory')
    accuracy = fields.Float(string='Accuracy')
