# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockLocation(models.Model): #osv.osv ??
    _inherit = 'stock.location'

    qty_variance_inventory_threshold = fields.Float('Acceptable Inventory '
                                                    'Quantity Variance '
                                                    'Threshold')
    last_inventory_adjustment = fields.Datetime('Last Inventory Adjustment')
    # TODO: add and define fields.


class StockWarehouse(models.Model): #osv.osv ??
    _inherit = 'stock.warehouse'

    cycle_count_rule_ids = fields.Many2many(
        comodel_name='stock.cycle.count.rule',
        relation='warehouse_cycle_count_'
                 'rule_rel',
        column1='warehouse_id',
        column2='rule_id',
        string='Cycle Count Rules')

    test_field = fields.Char('Testing')

    @api.model
    def _get_cycle_count_locations_search_domain(self, wh):
        wh_parent_left = wh.view_location_id.parent_left
        wh_parent_right = wh.view_location_id.parent_right
        domain = [('id', 'child_of', wh.view_location_id.id),
                  ('parent_left', '>', wh_parent_left),
                  ('parent_right', '<', wh_parent_right)]
        return domain

    @api.model
    def _search_cycle_count_locations(self, wh):
        locations = self.env['stock.location'].search(
            self._get_cycle_count_locations_search_domain(wh))
        return locations

    @api.multi
    def action_compute_cycle_count_rules(self):
        ''' Apply the rule in all the sublocations of a given warehouse(s) and
        returns a list with required dates for the cycle count of each
        location '''
        proposed_cycle_counts = []
        for wh in self:
            locations = self._search_cycle_count_locations(wh)
            if locations:
                self.test_field = locations
                for rule in wh.cycle_count_rule_ids:
                    # TODO: test with several rules.
                    proposed_cycle_counts.extend(rule.compute_rule(locations))
        if proposed_cycle_counts:
            # TODO: check if it works when duplicated location.
            locations = list(set([d['location'] for d in
                                  proposed_cycle_counts]))
            for loc in locations:
                # TODO: test with several proposals.
                proposed_for_loc = filter(lambda x: x['location'] == loc,
                                          proposed_cycle_counts)
                earliest_date = min([d['date'] for d in proposed_for_loc])
                cycle_count_proposed = filter(lambda x: x['date'] ==
                                              earliest_date,
                                              proposed_for_loc)[0]
                # TODO: add permitted states.
                domain = [('location_id', '=', loc.id),
                          ('state', 'in', ['draft'])]
                existing_cycle_counts = self.env['stock.cycle.count'].search(
                    domain)
                if existing_cycle_counts and cycle_count_proposed['date'] <\
                        existing_cycle_counts.date_deadline:
                    self.env['stock.cycle.count'].create({
                        'date_deadline': cycle_count_proposed['date'],
                        'location_id': cycle_count_proposed['location'].id,
                        'cycle_count_rule_id': cycle_count_proposed[
                            'rule_type'].id,
                        'state': 'draft'
                    })
                    existing_cycle_counts.state = 'cancelled'

                if not existing_cycle_counts:
                    self.env['stock.cycle.count'].create({
                        'date_deadline': cycle_count_proposed['date'],
                        'location_id': cycle_count_proposed['location'].id,
                        'cycle_count_rule_id': cycle_count_proposed[
                            'rule_type'].id,
                        'state': 'draft'
                    })


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    cycle_count_id = fields.Many2one(comodel_name='stock.cycle.count',
                                     string='Stock Cycle Count')
