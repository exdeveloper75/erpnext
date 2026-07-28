# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ConstructionEquipmentCost(Document):
	def validate(self):
		self.amount = flt(self.qty) * flt(self.rate)
		if self.project and not self.company:
			self.company = frappe.db.get_value("Project", self.project, "company")

	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Cancelled")
