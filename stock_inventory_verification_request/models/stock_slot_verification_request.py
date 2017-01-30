# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class SlotVerificationRequest(models.Model):
    _name = 'stock.slot.verification.request'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'stock.slot.verification.request') or ''
        return super(SlotVerificationRequest, self).create(vals)

    name = fields.Char(string='Name', readonly=True)
    inventory_id = fields.Many2one(comodel_name='stock.inventory',
                                   string='Inventory Adjustment', required=True)
    state = fields.Selection(selection=[
        ('wait', 'Waiting Actions'),
        ('open', 'In Progress'),
        ('cancelled', 'Cancelled'),
        ('done', 'Solved')
    ], string='Status', default='wait')
    responsible_id = fields.Many2one(comodel_name='res.users',
                                     string='Assigned to')
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product', required=True)
    notes = fields.Text('Notes')
    involved_location_ids = fields.Many2many(
        comodel_name='stock.location',
        relation='slot_verification_location_involved_rel',
        column1='slot_verification_request_id',
        column2='location_id',
        string='Involved Locations')

    @api.model
    def _get_involved_locs_domain(self):
        # TODO: debug this
        loc = self.inventory_id.location_id
        domain = [('product_id', '=', self.product_id), '|',
                  ('location_id', '=', loc),
                  ('location_dest_id', '=', loc)]
        return domain

    @api.model
    def _get_involved_locations(self):
        # TODO: debug this
        involved_moves = self.env['stock.move'].search(
            self._get_involved_locs_domain())
        involved_locs = involved_moves.mapped('location_id')
        return involved_locs

    @api.one
    def action_confirm(self):
        self.state = 'open'
        involved_locs = self._get_involved_locations()
        # TODO: is this the proper way?:
        self.involved_location_ids = involved_locs.ids
        return True

    @api.one
    def action_cancel(self):
        self.state = 'cancelled'
        return True

    @api.one
    def action_solved(self):
        self.state = 'done'
        return True
