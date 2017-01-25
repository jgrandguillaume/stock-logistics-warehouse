# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


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
                                     string='Stock Cycle Count',
                                     ondelete='cascade')
    loc_accuracy = fields.Float(string='Accuracy',
                                compute=_compute_loc_accuracy)

    @api.multi
    def action_done(self):
        if self.cycle_count_id:
            self.cycle_count_id.state = 'done'
        if self.filter == 'none':
            self.env['stock.inventory.history'].create({
                'location_id': self.location_id.id,
                'inventory_id': self.id,
                'accuracy': self.loc_accuracy
            })
        return super(StockInventory, self).action_done()
