# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import datetime


class StockLocation(models.Model):
    _inherit = 'stock.location'

    cycle_count_zero_confirmation = fields.Boolean(
        string='Zero Confirmation',
        help='Triggers a zero-confirmation validation when the location runs '
             'out of stock.')
    qty_variance_inventory_threshold = fields.Float('Acceptable Inventory '
                                                    'Quantity Variance '
                                                    'Threshold')
    last_inventory_adjustment = fields.Datetime('Last Inventory Adjustment')

    @api.model
    def _get_zero_confirmation_domain(self):
        domain = [('location_id', '=', self.id)]
        return domain

    @api.one
    def check_zero_confirmation(self):
        quants = self.env['stock.quant'].search(
            self._get_zero_confirmation_domain())
        if not quants:
            self.create_zero_confirmation_cycle_count()

    def create_zero_confirmation_cycle_count(self):
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        rule = self.env['stock.cycle.count.rule'].search([
            ('rule_type', '=', 'zero')])
        # TODO: add WH to domain: ('warehouse_ids', '=', self.id)?¿
        self.env['stock.cycle.count'].create({
            'date_deadline': date,
            'location_id': self.id,
            'cycle_count_rule_id': rule.id,
            'state': 'draft'
        })
        pass
