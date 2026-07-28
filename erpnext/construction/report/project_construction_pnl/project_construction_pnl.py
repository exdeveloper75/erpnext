# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.construction.utils import get_project_actuals_by_category, get_project_revenue_snapshot


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{"fieldname": "project", "label": _("Project"), "fieldtype": "Link", "options": "Project", "width": 140},
		{"fieldname": "project_name", "label": _("Project Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "contract_value", "label": _("Contract Value"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "certified_amount", "label": _("Certified"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "collected_amount", "label": _("Collected"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "outstanding_receivable", "label": _("Outstanding AR"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "materials", "label": _("Materials"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "labor", "label": _("Labor"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "equipment", "label": _("Equipment"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "subcontract", "label": _("Subcontract"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "expenses", "label": _("Expenses"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "total_cost", "label": _("Total Cost"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "gross_profit", "label": _("Gross Profit"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "margin_percent", "label": _("Margin %"), "fieldtype": "Percent", "width": 90},
	]


def get_data(filters):
	project_filters = {}
	if filters.get("company"):
		project_filters["company"] = filters.get("company")
	if filters.get("project"):
		project_filters["name"] = filters.get("project")

	projects = frappe.get_all(
		"Project",
		filters=project_filters,
		fields=["name", "project_name", "company", "status"],
		order_by="modified desc",
	)

	rows = []
	for p in projects:
		revenue = get_project_revenue_snapshot(project=p.name)
		actuals = get_project_actuals_by_category(p.name)
		total_cost = (
			flt(actuals["Materials"])
			+ flt(actuals["Labor"])
			+ flt(actuals["Equipment"])
			+ flt(actuals["Subcontract"])
			+ flt(actuals["Expenses"])
			+ flt(actuals["Other"])
		)
		contract_value = flt(revenue["contract_value"])
		gross_profit = contract_value - total_cost
		margin = (gross_profit / contract_value * 100.0) if contract_value else 0.0
		rows.append(
			{
				"project": p.name,
				"project_name": p.project_name,
				"contract_value": contract_value,
				"certified_amount": revenue["certified_amount"],
				"collected_amount": revenue["collected_amount"],
				"outstanding_receivable": revenue["outstanding_receivable"],
				"materials": actuals["Materials"],
				"labor": actuals["Labor"],
				"equipment": actuals["Equipment"],
				"subcontract": actuals["Subcontract"],
				"expenses": actuals["Expenses"],
				"total_cost": total_cost,
				"gross_profit": gross_profit,
				"margin_percent": margin,
			}
		)
	return rows


def get_chart(data):
	if not data:
		return None
	labels = [d.get("project_name") or d.get("project") for d in data][:12]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Contract Value"), "values": [flt(d["contract_value"]) for d in data[:12]]},
				{"name": _("Total Cost"), "values": [flt(d["total_cost"]) for d in data[:12]]},
				{"name": _("Gross Profit"), "values": [flt(d["gross_profit"]) for d in data[:12]]},
			],
		},
		"type": "bar",
	}


def get_summary(data):
	contract = sum(flt(d["contract_value"]) for d in data)
	cost = sum(flt(d["total_cost"]) for d in data)
	profit = sum(flt(d["gross_profit"]) for d in data)
	return [
		{"value": contract, "label": _("Contract Value"), "datatype": "Currency"},
		{"value": cost, "label": _("Total Cost"), "datatype": "Currency"},
		{"value": profit, "label": _("Gross Profit"), "datatype": "Currency"},
	]
