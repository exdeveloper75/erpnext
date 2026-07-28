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

	@frappe.whitelist()
	def create_project(self):
		"""Create Project from contract (عقد أولاً ثم مشروع)."""
		if self.project:
			frappe.throw(frappe._("Project {0} is already linked").format(self.project))
		if self.docstatus != 1:
			frappe.throw(frappe._("Submit the contract before creating a project"))
		if self.contract_type != "Customer":
			frappe.throw(frappe._("Create Project is only for Customer contracts"))

		project = frappe.new_doc("Project")
		project.project_name = self.title
		project.company = self.company
		project.customer = self.party
		project.expected_start_date = self.start_date
		project.expected_end_date = self.end_date
		project.insert()

		self.db_set("project", project.name)
		return project.name
