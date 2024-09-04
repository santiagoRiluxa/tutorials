from odoo import models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        # Call the super method to retain original behavior
        result = super(EstateProperty, self).action_sold()

        # Define move_type and journal_id
        move_type = 'out_invoice'  # Customer Invoice
        journal_id = self.env.ref('account.sales_journal').id  # Replace with your journal's XML ID

        for property in self:
            # Ensure partner_id and journal_id are present
            if not property.partner_id:
                raise ValueError("The property must have a partner assigned before creating an invoice.")
            if not journal_id:
                raise ValueError("No accounting journal found for creating an invoice.")
            if not property.selling_price:
                raise ValueError("The property must have a selling price before creating an invoice.")

            # Calculate the amount for the 6% fee and the administrative fee
            percentage_amount = property.selling_price * 0.06
            admin_fees = 100.00

            # Create the invoice
            self.env['account.move'].create({
                'partner_id': property.partner_id.id,
                'move_type': move_type,
                'journal_id': journal_id,
                'state': 'draft',  # Invoice starts in draft state
                'invoice_line_ids': [(0, 0, {
                    'name': 'Property Sale Commission (6%)',
                    'quantity': 1,
                    'price_unit': percentage_amount,
                }), (0, 0, {
                    'name': 'Administrative Fees',
                    'quantity': 1,
                    'price_unit': admin_fees,
                })]
            })

        return result
