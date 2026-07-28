# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

from erpnext.construction.utils import (
	get_contract_boq_items,
	get_invoice_collection,
	get_previous_certified_amount,
)


class CustomerPaymentCertificate(Document):
	def validate(self):
		self.set_previous_certified()
		self.calculate_totals()
		self.refresh_collection()

	def set_previous_certified(self):
		self.previous_certified_amount = get_previous_certified_amount(
			"Customer Payment Certificate",
			contract=self.construction_contract,
			project=self.project,
			exclude=self.name,
		)

	def calculate_totals(self):
		gross = 0.0
		for row in self.items or []:
			row.cumulative_qty = flt(row.previous_qty) + flt(row.current_qty)
			row.current_amount = flt(row.current_qty) * flt(row.rate)
			gross += flt(row.current_amount)

		self.gross_amount = gross
		self.retention_amount = flt(gross) * flt(self.retention_percent) / 100.0
		self.claimed_amount = (
			flt(gross)
			- flt(self.retention_amount)
			- flt(self.advance_recovery)
			+ flt(self.retention_release)
		)
		if not flt(self.approved_amount):
			self.approved_amount = self.claimed_amount

	def refresh_collection(self):
		info = get_invoice_collection("Sales Invoice", self.sales_invoice)
		self.collected_amount = info["collected_amount"]
		self.outstanding_amount = info["outstanding_amount"]
		self.collection_status = info["collection_status"]

	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	@frappe.whitelist()
	def get_items_from_contract(self):
		if not self.construction_contract:
			frappe.throw(frappe._("Select a Construction Contract first"))
		rows = get_contract_boq_items(
			self.construction_contract,
			certificate_doctype="Customer Payment Certificate",
			exclude=self.name,
		)
		self.set("items", [])
		for row in rows:
			self.append("items", row)
		self.calculate_totals()
		return len(rows)

	@frappe.whitelist()
	def mark_approved(self):
		if self.docstatus != 1:
			frappe.throw(frappe._("Submit the certificate before approving"))
		if not flt(self.approved_amount):
			self.db_set("approved_amount", self.claimed_amount)
		self.db_set("status", "Approved")

	@frappe.whitelist()
	def create_sales_invoice(self):
		if self.sales_invoice:
			frappe.throw(frappe._("Sales Invoice {0} already linked").format(self.sales_invoice))
		if self.docstatus != 1:
			frappe.throw(frappe._("Submit the certificate before creating an invoice"))

		bill_amount = flt(self.approved_amount) or flt(self.claimed_amount)
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
				"rate": bill_amount,
				"amount": bill_amount,
				"income_account": company.default_income_account,
				"cost_center": company.cost_center,
			},
		)
		invoice.insert()
		self.db_set("sales_invoice", invoice.name)
		self.db_set("status", "Invoiced")
		info = get_invoice_collection("Sales Invoice", invoice.name)
		self.db_set("collected_amount", info["collected_amount"])
		self.db_set("outstanding_amount", info["outstanding_amount"])
		self.db_set("collection_status", info["collection_status"])
		return invoice.name
