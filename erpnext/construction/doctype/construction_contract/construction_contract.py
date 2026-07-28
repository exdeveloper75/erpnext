# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ConstructionContract(Document):
	def validate(self):
		self.set_party_type_from_contract_type()
		self.calculate_totals()

	def set_party_type_from_contract_type(self):
		if self.contract_type == "Customer":
			self.party_type = "Customer"
		elif self.contract_type == "Contractor":
			self.party_type = "Supplier"

	def calculate_totals(self):
		total = 0.0
		for row in self.items or []:
			row.amount = flt(row.qty) * flt(row.rate)
			total += flt(row.amount)
		self.total_amount = total
		if not self.contract_value:
			self.contract_value = total

	def on_submit(self):
		self.db_set("status", "Active")

	def on_cancel(self):
		self.db_set("status", "Cancelled")
