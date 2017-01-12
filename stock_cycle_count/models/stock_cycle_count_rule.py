# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _, exceptions
from datetime import timedelta, datetime


class StockCycleCountRule(models.Model):
    _name = 'stock.cycle.count.rule'

    @api.model
    def _selection_rule_types(self):
        return [
            ('periodic', _('Periodic'))]

    def compute_rule(self, locs):
        if self.rule_type == 'periodic':
            proposed_cycle_counts = self._compute_rule_periodic(locs)
        return proposed_cycle_counts

    @api.model
    def _compute_rule_periodic(self, locs):
        cycle_counts = []
        for loc in locs:
            last_inventories = self.env['stock.inventory'].search([
                ('location_id', '=', loc.id),
                ('state', 'in', ['confirm', 'done', 'draft'])]).mapped('date')
            if last_inventories:
                latest_inventory = sorted(last_inventories, reverse=True)[0]
                try:
                    period = self.periodic_count_period / \
                             self.periodic_qty_per_period
                    next_date = datetime.strptime(
                        latest_inventory, '%Y-%m-%d %H:%M:%S') + timedelta(
                        days=period)
                except Exception as e:
                    raise exceptions.UserError(_('Error found determining the '
                                                 'frequency of periodic cycle '
                                                 'count rule. %s') % e.message)
            else:
                next_date = datetime.today()
            cycle_count = {
                'date': next_date.strftime('%Y-%m-%d %H:%M:%S'),
                'location': loc,
                'rule_type': self
            }
            cycle_counts.append(cycle_count)
        return cycle_counts

    name = fields.Char('Name')
    rule_type = fields.Selection(selection="_selection_rule_types",
                                 string='Type of rule',
                                 required=True)
    periodic_qty_per_period = fields.Integer(string='Counts per period')
    periodic_count_period = fields.Integer(string='Period in days')
    max_days_without_cc = fields.Integer('Max. interval',
                                         help='Maximum of days without '
                                              'performing an inventory '
                                              'adjustment')
    warehouse_ids = fields.Many2many(comodel_name='stock.warehouse',
                                     relation='warehouse_cycle_count_rule_rel',
                                     column1='rule_id',
                                     column2='warehouse_id',
                                     string='Applied in')
