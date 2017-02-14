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

    @api.multi
    def action_request_verification(self):
        self.requested_verification = True
        for line in self.line_ids:
            if line.discrepancy_threshold and (line.discrepancy_percent >
                                               line.discrepancy_threshold):
                self.env['stock.slot.verification.request'].create({
                    'inventory_id': self.id,
                    'inventory_line_id': line.id,
                    'location_id': self.location_id.id,
                    'state': 'wait',
                    'product_id': line.product_id.id,
                })
