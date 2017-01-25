# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.one
    def _compute_loc_accuracy(self):
        total_qty = sum(self.line_ids.mapped('theoretical_qty'))
        abs_discrepancy = sum(self.line_ids.mapped(
            lambda x: abs(x.discrepancy_qty)))
        if total_qty:
            self.loc_accuracy = (total_qty - abs_discrepancy) / total_qty

    cycle_count_id = fields.Many2one(comodel_name='stock.cycle.count',
                                     string='Stock Cycle Count')
    loc_accuracy = fields.Float(string='Accuracy',
                                compute=_compute_loc_accuracy)

    @api.model
    def action_over_discrepancies(self, data):
        raise UserError(
            _('Cannot validate the Inventory Adjustment.\n Found %s over '
              'discrepancies') % data
        )

    @api.multi
    def action_done(self):
        discrepancies = self.line_ids.mapped('discrepancy_percentage')
        wh_id = self.location_id.get_warehouse(self.location_id)
        wh = self.env['stock.warehouse'].browse(wh_id)
        if self.location_id.discrepancy_threshold > 0.0:
            threshold = self.location_id.discrepancy_threshold
        elif wh.discrepancy_threshold > 0.0:
            threshold = wh.discrepancy_threshold
        else:
            return super(StockInventory, self).action_done()
        if threshold:
            over_discrepancies = sum(d > threshold for d in discrepancies)
            if over_discrepancies:
                self.action_over_discrepancies(over_discrepancies)
            else:
                return super(StockInventory, self).action_done()
