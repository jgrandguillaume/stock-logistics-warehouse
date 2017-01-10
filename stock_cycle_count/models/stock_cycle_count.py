# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import timedelta, datetime


class StockCycleCount(models.Model):

    _name = 'stock.cycle.count'

    @api.one
    def _get_name(self):
        self.name = 'CC/{}/{}'.format(self.location_id.name,
                                      self.cycle_count_rule_id.name)

    @api.one
    def do_cancel(self):
        self.state = 'cancelled'

    @api.one
    def _prepare_inventory_adjustment(self):
        return {
            'name': '{} inventory ({})'.format(self.location_id.name,
                                               self.name),
            'cycle_count_id': self.id,
            'location_id': self.location_id.id
        }

    @api.one
    def action_create_inventory_adjustment(self):
        self.env['stock.inventory'].create(
            self._prepare_inventory_adjustment(self))
        self.state = 'open'
        return True

    @api.one
    def action_view_inventory(self):
        domain = []
        return {
            'name': 'Associated Inventory Adjustment',
            'domain': domain,
            'res_model': 'stock.inventory',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'tree',
        }

    name = fields.Char(string='Name',
                       compute=_get_name)
    # TODO: compute name.
    location_id = fields.Many2one(comodel_name='stock.location',
                                  string='Location',
                                  required=True)
    responsible_id = fields.Many2one(comodel_name='res.users',
                                     string='Assigned to')
    date_deadline = fields.Datetime(string='Required Date')
    cycle_count_rule_id = fields.Many2one(comodel_name='stock.cycle.count.rule',
                                          string='Cycle count rule',
                                          required=True)
    state = fields.Selection(selection=[
        ('draft', 'Planned'),
        ('open', 'Execution'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done')
    ], string='State', default='draft')
    stock_adjustment_ids = fields.One2many(comodel_name='stock.inventory',
                                           inverse_name='cycle_count_id',
                                           string='Inventory Adjustment')
