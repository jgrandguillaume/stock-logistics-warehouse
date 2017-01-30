# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    requested_verification = fields.Boolean(string='Requested Verification?',
                                            default=False)
    slot_verification_ids = fields.One2many(
        comodel_name='stock.slot.verification.request',
        string='Slot Verification Requests', inverse_name='inventory_id')

    @api.model
    def _get_threshold_for_overdiscrepancies(self):
        threshold = 0.0
        wh_id = self.location_id.get_warehouse(self.location_id)
        wh = self.env['stock.warehouse'].browse(wh_id)
        if self.location_id.discrepancy_threshold > 0.0:
            threshold = self.location_id.discrepancy_threshold
        elif wh.discrepancy_threshold > 0.0:
            threshold = wh.discrepancy_threshold
        else:
            pass
        return threshold

    @api.multi
    def action_request_verification(self):
        self.requested_verification = True
        threshold = self._get_threshold_for_overdiscrepancies()
        for line in self.line_ids:
            if threshold and line.discrepancy_percentage > threshold:
                self.env['stock.slot.verification.request'].create({
                    'inventory_id': self.id,
                    'state': 'wait',
                    'product_id': line.product_id.id,
                })
