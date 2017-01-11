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
    def _count_inventory_adj(self):
        self.inventory_adj_count = len(self.stock_adjustment_ids)

    name = fields.Char(string='Name',
                       compute=_get_name)
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
    inventory_adj_count = fields.Integer(compute=_count_inventory_adj)

    @api.one
    def do_cancel(self):
        self.state = 'cancelled'

    @api.model
    def _prepare_inventory_adjustment(self):
        return {
            'name': self.name,
            'cycle_count_id': self.id,
            'location_id': self.location_id.id
        }

    @api.one
    def action_create_inventory_adjustment(self):
        data = self._prepare_inventory_adjustment()
        self.env['stock.inventory'].create(data)
        self.state = 'open'
        return True

    @api.multi
    def action_view_inventory(self):
        action = self.env.ref('stock.action_inventory_form')
        result = action.read()[0]
        result['context'] = {}
        adjustment_ids = sum([cycle_count.stock_adjustment_ids.ids
                              for cycle_count in self], [])
        if len(adjustment_ids) > 1:
            result['domain'] = \
                "[('id','in',[" + ','.join(map(str, adjustment_ids)) + "])]"
        elif len(adjustment_ids) == 1:
            res = self.env.ref('stock.view_inventory_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = adjustment_ids and adjustment_ids[0] or False
        return result
