# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

from erpnext.construction.utils import get_project_actuals_by_category, get_project_revenue_snapshot


class ConstructionProjectBudget(Document):
	def validate(self):
		self.ensure_unique_project()
		self.set_defaults_from_links()
		self.refresh_snapshot(save_actuals=True)
		self.calculate_totals()

	def ensure_unique_project(self):
		if not self.project:
			return
		existing = frappe.db.exists(
			"Construction Project Budget",
			{"project": self.project, "docstatus": ["<", 2], "name": ["!=", self.name]},
		)
		if existing:
			frappe.throw(
				frappe._("Project {0} already has budget {1}").format(self.project, existing)
			)

	def set_defaults_from_links(self):
		if self.project and not self.title:
			self.title = frappe.db.get_value("Project", self.project, "project_name") or self.project
		if self.project and not self.company:
			self.company = frappe.db.get_value("Project", self.project, "company")
		if self.construction_contract and not self.currency:
			self.currency = frappe.db.get_value(
				"Construction Contract", self.construction_contract, "currency"
			)
		if not self.currency and self.company:
			self.currency = frappe.get_cached_value("Company", self.company, "default_currency")
		if self.project and not self.construction_contract:
			contract = frappe.db.get_value(
				"Construction Contract",
				{"project": self.project, "docstatus": 1, "contract_type": "Customer"},
				"name",
			)
			if contract:
				self.construction_contract = contract

	def refresh_snapshot(self, save_actuals=False):
		revenue = get_project_revenue_snapshot(self.project, self.construction_contract)
		self.contract_value = revenue["contract_value"]
		self.certified_amount = revenue["certified_amount"]
		self.collected_amount = revenue["collected_amount"]
		self.outstanding_receivable = revenue["outstanding_receivable"]

		if save_actuals:
			actuals = get_project_actuals_by_category(self.project)
			for row in self.items or []:
				row.actual_amount = flt(actuals.get(row.cost_category))
				row.variance = flt(row.budget_amount) - flt(row.actual_amount)

	def calculate_totals(self):
		total_budget = 0.0
		total_actual = 0.0
		for row in self.items or []:
			row.variance = flt(row.budget_amount) - flt(row.actual_amount)
			total_budget += flt(row.budget_amount)
			total_actual += flt(row.actual_amount)
		self.total_budget = total_budget
		self.total_actual = total_actual
		self.budget_variance = total_budget - total_actual
		self.estimated_profit = flt(self.contract_value) - total_actual

	def on_submit(self):
		self.db_set("status", "Active")

	def on_cancel(self):
		self.db_set("status", "Cancelled")

	@frappe.whitelist()
	def refresh_actuals(self):
		self.refresh_snapshot(save_actuals=True)
		self.calculate_totals()
		self.save()
		return {
			"total_budget": self.total_budget,
			"total_actual": self.total_actual,
			"budget_variance": self.budget_variance,
			"estimated_profit": self.estimated_profit,
			"certified_amount": self.certified_amount,
			"collected_amount": self.collected_amount,
		}
