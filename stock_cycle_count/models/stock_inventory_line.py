# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.one
    def _compute_accuracy(self):
        if self.theoretical_qty:
            self.accuracy = (self.theoretical_qty - abs(self.product_qty -
                self.theoretical_qty)) / self.theoretical_qty

    accuracy = fields.Float(string='Accuracy', compute=_compute_accuracy)
