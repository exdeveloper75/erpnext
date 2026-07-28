# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.utils import flt


def get_previous_certified_amount(doctype, contract=None, project=None, exclude=None):
	"""Sum approved amounts of prior submitted certificates for same contract/project."""
	filters = {"docstatus": 1, "name": ["!=", exclude]} if exclude else {"docstatus": 1}
	if contract:
		filters["construction_contract"] = contract
	elif project:
		filters["project"] = project
	else:
		return 0.0

	rows = frappe.get_all(
		doctype, filters=filters, fields=["approved_amount", "claimed_amount"]
	)
	total = 0.0
	for row in rows:
		total += flt(row.approved_amount or row.claimed_amount)
	return total


def get_invoice_collection(doctype, invoice_name):
	"""Return collected, outstanding, and status label from a Sales/Purchase Invoice."""
	if not invoice_name:
		return {
			"collected_amount": 0.0,
			"outstanding_amount": 0.0,
			"collection_status": "Not Invoiced",
		}

	meta = {
		"Sales Invoice": ("grand_total", "outstanding_amount", "status"),
		"Purchase Invoice": ("grand_total", "outstanding_amount", "status"),
	}
	fields = meta.get(doctype)
	if not fields:
		return {
			"collected_amount": 0.0,
			"outstanding_amount": 0.0,
			"collection_status": "Not Invoiced",
		}

	inv = frappe.db.get_value(doctype, invoice_name, fields, as_dict=True)
	if not inv:
		return {
			"collected_amount": 0.0,
			"outstanding_amount": 0.0,
			"collection_status": "Not Invoiced",
		}

	grand = flt(inv.get(fields[0]))
	outstanding = flt(inv.get(fields[1]))
	collected = max(grand - outstanding, 0.0)
	status = inv.get(fields[2]) or ""

	if outstanding <= 0 and grand > 0:
		label = "Paid"
	elif collected > 0:
		label = "Partially Paid"
	elif status in ("Unpaid", "Overdue", "Partly Paid"):
		label = "Unpaid" if collected <= 0 else "Partially Paid"
	else:
		label = "Unpaid"

	return {
		"collected_amount": collected,
		"outstanding_amount": outstanding,
		"collection_status": label,
	}


def get_project_revenue_snapshot(project=None, contract=None):
	"""Contract value + customer certificate certified/collected for a project."""
	contract_value = 0.0
	if contract:
		contract_value = flt(frappe.db.get_value("Construction Contract", contract, "contract_value"))
	elif project:
		contract_value = flt(
			frappe.db.get_value(
				"Construction Contract",
				{"project": project, "docstatus": 1, "contract_type": "Customer"},
				"contract_value",
			)
		)
		if not contract_value:
			contract_value = flt(frappe.db.get_value("Project", project, "estimated_costing"))

	certified = get_previous_certified_amount(
		"Customer Payment Certificate", contract=contract, project=project
	)

	collected = 0.0
	outstanding = 0.0
	filters = {"docstatus": 1, "sales_invoice": ["is", "set"]}
	if contract:
		filters["construction_contract"] = contract
	elif project:
		filters["project"] = project
	else:
		return {
			"contract_value": contract_value,
			"certified_amount": certified,
			"collected_amount": 0.0,
			"outstanding_receivable": 0.0,
		}

	for row in frappe.get_all(
		"Customer Payment Certificate", filters=filters, fields=["sales_invoice"]
	):
		info = get_invoice_collection("Sales Invoice", row.sales_invoice)
		collected += flt(info["collected_amount"])
		outstanding += flt(info["outstanding_amount"])

	return {
		"contract_value": contract_value,
		"certified_amount": certified,
		"collected_amount": collected,
		"outstanding_receivable": outstanding,
	}


def get_project_actuals_by_category(project):
	"""Actual cost by construction category for a project."""
	actuals = {
		"Materials": 0.0,
		"Labor": 0.0,
		"Equipment": 0.0,
		"Subcontract": 0.0,
		"Expenses": 0.0,
		"Other": 0.0,
	}
	if not project:
		return actuals

	proj = frappe.db.get_value(
		"Project",
		project,
		["total_consumed_material_cost", "total_purchase_cost", "total_costing_amount"],
		as_dict=True,
	) or {}
	actuals["Materials"] = flt(proj.get("total_consumed_material_cost")) or flt(
		proj.get("total_purchase_cost")
	)

	timesheet_labor = flt(
		frappe.db.sql(
			"""
			select sum(total_costing_amount)
			from `tabTimesheet`
			where project=%s and docstatus=1
			""",
			project,
		)[0][0]
	)
	labor_entries = 0.0
	if frappe.db.exists("DocType", "Construction Labor Cost"):
		labor_entries = flt(
			frappe.db.sql(
				"""
				select sum(amount) from `tabConstruction Labor Cost`
				where project=%s and docstatus=1
				""",
				project,
			)[0][0]
		)
	actuals["Labor"] = timesheet_labor + labor_entries

	if frappe.db.exists("DocType", "Construction Equipment Cost"):
		actuals["Equipment"] = flt(
			frappe.db.sql(
				"""
				select sum(amount) from `tabConstruction Equipment Cost`
				where project=%s and docstatus=1
				""",
				project,
			)[0][0]
		)

	actuals["Subcontract"] = get_previous_certified_amount(
		"Contractor Payment Certificate", project=project
	)

	assigned = (
		actuals["Materials"]
		+ actuals["Labor"]
		+ actuals["Equipment"]
		+ actuals["Subcontract"]
	)
	residual = max(flt(proj.get("total_costing_amount")) - assigned, 0.0)
	actuals["Expenses"] = residual

	return actuals


def get_prior_certificate_qty(doctype, contract, description, rate, exclude=None):
	"""Sum previous current_qty on certificate items matched by description + rate."""
	if not contract:
		return 0.0

	parent_filters = {"docstatus": 1, "construction_contract": contract}
	if exclude:
		parent_filters["name"] = ["!=", exclude]
	parents = frappe.get_all(doctype, filters=parent_filters, pluck="name")
	if not parents:
		return 0.0

	total = 0.0
	for row in frappe.get_all(
		"Payment Certificate Item",
		filters={"parent": ["in", parents], "parenttype": doctype},
		fields=["description", "rate", "current_qty"],
	):
		if (row.description or "").strip() == (description or "").strip() and flt(row.rate) == flt(
			rate
		):
			total += flt(row.current_qty)
	return total


@frappe.whitelist()
def get_contract_boq_items(contract, certificate_doctype=None, exclude=None):
	"""Return BOQ lines from Construction Contract with previous qty for certificates."""
	if not contract:
		return []

	items = frappe.get_all(
		"Construction Contract Item",
		filters={"parent": contract},
		fields=["description", "uom", "qty", "rate", "idx"],
		order_by="idx asc",
	)
	certificate_doctype = certificate_doctype or "Customer Payment Certificate"
	rows = []
	for item in items:
		previous_qty = get_prior_certificate_qty(
			certificate_doctype,
			contract,
			item.description,
			item.rate,
			exclude=exclude,
		)
		rows.append(
			{
				"description": item.description,
				"uom": item.uom,
				"contract_qty": item.qty,
				"previous_qty": previous_qty,
				"current_qty": 0,
				"rate": item.rate,
			}
		)
	return rows
