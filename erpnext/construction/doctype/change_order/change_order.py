# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from frappe.model.document import Document
from frappe.utils import flt


class ChangeOrder(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		total = 0.0
		for row in self.items or []:
			row.amount = flt(row.qty) * flt(row.rate)
			total += flt(row.amount)
		self.total_amount = total

	def on_submit(self):
		self.db_set("status", "Approved")

	def on_cancel(self):
		self.db_set("status", "Cancelled")
