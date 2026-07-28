# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.construction.utils import get_project_revenue_snapshot


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	summary = get_summary(data)
	return columns, data, None, None, summary


def get_columns():
	return [
		{"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 160},
		{"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "contracts", "label": _("Contracts"), "fieldtype": "Int", "width": 90},
		{"fieldname": "projects", "label": _("Projects"), "fieldtype": "Int", "width": 90},
		{"fieldname": "change_orders", "label": _("Change Orders"), "fieldtype": "Int", "width": 110},
		{"fieldname": "contract_value", "label": _("Contract Value"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "certified_amount", "label": _("Certified"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "collected_amount", "label": _("Collected"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "outstanding_receivable", "label": _("Outstanding AR"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	customer_filters = {}
	if filters.get("customer"):
		customer_filters["name"] = filters.get("customer")

	customers = frappe.get_all(
		"Customer",
		filters=customer_filters,
		fields=["name", "customer_name"],
		order_by="customer_name asc",
		limit_page_length=500,
	)

	rows = []
	for c in customers:
		contracts = frappe.get_all(
			"Construction Contract",
			filters={"party": c.name, "contract_type": "Customer", "docstatus": ["<", 2]},
			fields=["name", "project", "contract_value", "docstatus"],
		)
		if not contracts and not filters.get("customer"):
			continue

		projects = {row.project for row in contracts if row.project}
		# also projects linked via customer field on Project
		for p in frappe.get_all("Project", filters={"customer": c.name}, pluck="name"):
			projects.add(p)

		change_orders = 0
		if projects:
			change_orders = frappe.db.count(
				"Change Order", {"project": ["in", list(projects)], "docstatus": ["<", 2]}
			)

		contract_value = sum(flt(row.contract_value) for row in contracts if row.docstatus == 1)
		certified = collected = outstanding = 0.0
		for project in projects:
			rev = get_project_revenue_snapshot(project=project)
			certified += flt(rev["certified_amount"])
			collected += flt(rev["collected_amount"])
			outstanding += flt(rev["outstanding_receivable"])

		# contracts without project still count certified via contract link
		for row in contracts:
			if row.docstatus != 1 or row.project:
				continue
			rev = get_project_revenue_snapshot(contract=row.name)
			certified += flt(rev["certified_amount"])
			collected += flt(rev["collected_amount"])
			outstanding += flt(rev["outstanding_receivable"])
			contract_value = max(contract_value, contract_value)  # already summed

		rows.append(
			{
				"customer": c.name,
				"customer_name": c.customer_name,
				"contracts": len(contracts),
				"projects": len(projects),
				"change_orders": change_orders,
				"contract_value": contract_value,
				"certified_amount": certified,
				"collected_amount": collected,
				"outstanding_receivable": outstanding,
			}
		)
	return rows


def get_summary(data):
	return [
		{"value": sum(flt(d["contract_value"]) for d in data), "label": _("Contract Value"), "datatype": "Currency"},
		{"value": sum(flt(d["certified_amount"]) for d in data), "label": _("Certified"), "datatype": "Currency"},
		{"value": sum(flt(d["collected_amount"]) for d in data), "label": _("Collected"), "datatype": "Currency"},
		{
			"value": sum(flt(d["outstanding_receivable"]) for d in data),
			"label": _("Outstanding AR"),
			"datatype": "Currency",
		},
	]
