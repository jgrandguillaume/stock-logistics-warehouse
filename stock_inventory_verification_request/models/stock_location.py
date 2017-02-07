# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.one
    def _get_context_product_qty(self):
        if self._context.get('product_id'):
            quants = self.env['stock.quant'].search([
                ('product_id', '=', self._context['product_id']),
                ('location_id', '=', self.id)])
            if quants:
                self.product_qty = sum(quants.mapped('qty'))
            else:
                self.product_qty = 0.0

    @api.one
    def _get_context_product_uom(self):
        if self._context.get('product_id'):
            self.product_uom = self.env['product.product'].browse(
                self._context['product_id']).uom_id

    product_qty = fields.Float(string='Product Quantity',
                               compute=_get_context_product_qty)
    product_uom = fields.Many2one(comodel_name='product.uom',
                                  string='Product Unit of Measure',
                                  compute=_get_context_product_uom)
