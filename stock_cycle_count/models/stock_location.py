# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import datetime


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.one
    def _compute_loc_accuracy(self):
        history = self.env['stock.inventory.history'].search([
            ('location_id', '=', self.id)]).sorted(key=lambda r: r.write_date,
                                                   reverse=True)
        if history:
            self.loc_accuracy = history[0].accuracy

    cycle_count_zero_confirmation = fields.Boolean(
        string='Zero Confirmation',
        help='Triggers a zero-confirmation validation when the location runs '
             'out of stock.')
    qty_variance_inventory_threshold = fields.Float('Acceptable Inventory '
                                                    'Quantity Variance '
                                                    'Threshold')
    last_inventory_adjustment = fields.Datetime('Last Inventory Adjustment')
    loc_accuracy = fields.Float(string='Inventory Accuracy',
                                compute=_compute_loc_accuracy)

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
        wh_id = self.get_warehouse(self)
        date_horizon = self.env['stock.warehouse'].browse(
            wh_id).get_horizon_date()[0].strftime('%Y-%m-%d %H:%M:%S')
        counts_planned = self.env['stock.cycle.count'].search([
            ('date_deadline', '<', date_horizon), ('state', '=', 'draft'),
            ('location_id', '=', self.id)])
        if counts_planned:
            counts_planned.write({'state': 'cancelled'})
        rule = self.env['stock.cycle.count.rule'].search([
            ('rule_type', '=', 'zero'), ('warehouse_ids', '=', wh_id)])
        self.env['stock.cycle.count'].create({
            'date_deadline': date,
            'location_id': self.id,
            'cycle_count_rule_id': rule.id,
            'state': 'draft'
        })
        return True
