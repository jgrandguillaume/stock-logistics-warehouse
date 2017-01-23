# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from datetime import timedelta, datetime


class StockCycleCountRule(models.Model):
    _name = 'stock.cycle.count.rule'

    @api.one
    def _compute_currency(self):
        self.currency_id = self.env.user.company_id.currency_id

    @api.model
    def _selection_rule_types(self):
        return [
            ('periodic', _('Periodic')),
            ('turnover', _('Value Turnover')),
            ('zero', _('Zero Confirmation'))]

    @api.one
    @api.constrains('rule_type', 'warehouse_ids')
    def _check_zero_rule(self):
        if self.rule_type == 'zero' and len(self.warehouse_ids) > 1:
            raise UserError(
                _('Zero confirmation rules can only have one warehouse '
                  'assigned.')
            )
        zero_rule = self.search([
            ('rule_type', '=', 'zero'),
            ('warehouse_ids', '=', self.warehouse_ids.id), '|',
            ('active', '=', True), ('active', '=', False)])
        if len(zero_rule) > 1:
            raise UserError(
                _('You can only have one zero confirmation rule per '
                  'warehouse \nIf you do not see any, it may be inactive. '
                  'You can reactivate a zero confirmation rule from the '
                  'warehouse view.')
            )

    name = fields.Char('Name')
    rule_type = fields.Selection(selection="_selection_rule_types",
                                 string='Type of rule',
                                 required=True)
    active = fields.Boolean(string='Active', default=True)
    periodic_qty_per_period = fields.Integer(string='Counts per period')
    periodic_count_period = fields.Integer(string='Period in days')
    turnover_inventory_value_threshold = fields.Float(
        string='Turnover Inventory Value Threshold')
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  compute=_compute_currency)
    warehouse_ids = fields.Many2many(comodel_name='stock.warehouse',
                                     relation='warehouse_cycle_count_rule_rel',
                                     column1='rule_id',
                                     column2='warehouse_id',
                                     string='Applied in')

    def compute_rule(self, locs):
        if self.rule_type == 'periodic':
            proposed_cycle_counts = self._compute_rule_periodic(locs)
        elif self.rule_type == 'turnover':
            proposed_cycle_counts = self._compute_rule_turnover(locs)
        return proposed_cycle_counts

    @api.model
    def _propose_cycle_count(self, date, location):
        cycle_count = {
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'location': location,
            'rule_type': self
        }
        return cycle_count

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
                    raise UserError(
                        _('Error found determining the frequency of periodic '
                          'cycle count rule. %s') % e.message)
            else:
                next_date = datetime.today()
            cycle_count = self._propose_cycle_count(next_date, loc)
            cycle_counts.append(cycle_count)
        return cycle_counts

    @api.model
    def _get_turnover_moves(self, location, date):
        moves = self.env['stock.move'].search([
            '|', ('location_id', '=', location.id),
            ('location_dest_id', '=', location.id),
            ('date', '>', date),
            ('state', '=', 'done')])
        return moves

    @api.model
    def _compute_turnover(self, move):
        turnover = move.product_uom_qty * move.product_id.standard_price
        return turnover

    @api.model
    def _compute_rule_turnover(self, locs):
        cycle_counts = []
        for loc in locs:
            last_inventories = self.env['stock.inventory'].search([
                ('location_id', '=', loc.id),
                ('state', 'in', ['confirm', 'done', 'draft'])]).mapped('date')
            if last_inventories:
                latest_inventory = sorted(last_inventories, reverse=True)[0]
                moves = self._get_turnover_moves(loc, latest_inventory)
                if moves:
                    total_turnover = 0.0
                    for m in moves:
                        # TODO: is necessary to take into calculation the type of pricing?
                        turnover = self._compute_turnover(m)
                        total_turnover += turnover
                    try:
                        if total_turnover > \
                                self.turnover_inventory_value_threshold:
                            next_date = datetime.today()
                            cycle_count = self._propose_cycle_count(next_date,
                                                                    loc)
                            cycle_counts.append(cycle_count)
                    except Exception as e:
                        raise UserError(_(
                            'Error found when comparing turnover with the rule '
                            'threshold. %s') % e.message)
            else:
                next_date = datetime.today()
                cycle_count = self._propose_cycle_count(next_date, loc)
                cycle_counts.append(cycle_count)
        return cycle_counts

