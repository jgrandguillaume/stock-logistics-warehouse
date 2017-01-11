# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    qty_variance_inventory_threshold = fields.Float('Acceptable Inventory '
                                                    'Quantity Variance '
                                                    'Threshold')
    last_inventory_adjustment = fields.Datetime('Last Inventory Adjustment')
    # TODO: add and define fields.
