# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CustomerPaymentCertificate(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		gross = 0.0
		for row in self.items or []:
			row.cumulative_qty = flt(row.previous_qty) + flt(row.current_qty)
			row.current_amount = flt(row.current_qty) * flt(row.rate)
			gross += flt(row.current_amount)

		self.gross_amount = gross
		self.retention_amount = flt(gross) * flt(self.retention_percent) / 100.0
		self.net_amount = flt(gross) - flt(self.retention_amount) - flt(self.advance_recovery)

	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	@frappe.whitelist()
	def create_sales_invoice(self):
		if self.sales_invoice:
			frappe.throw(frappe._("Sales Invoice {0} already linked").format(self.sales_invoice))
		if self.docstatus != 1:
			frappe.throw(frappe._("Submit the certificate before creating an invoice"))

		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = self.customer
		invoice.company = self.company
		invoice.project = self.project
		invoice.currency = self.currency
		invoice.posting_date = self.posting_date
		company = frappe.get_cached_doc("Company", self.company)
		invoice.append(
			"items",
			{
				"item_name": self.title or "Customer Payment Certificate",
				"description": frappe._("Payment Certificate {0}").format(self.name),
				"qty": 1,
				"rate": self.net_amount,
				"amount": self.net_amount,
				"income_account": company.default_income_account,
				"cost_center": company.cost_center,
			},
		)
		invoice.insert()
		self.db_set("sales_invoice", invoice.name)
		self.db_set("status", "Invoiced")
		return invoice.name
