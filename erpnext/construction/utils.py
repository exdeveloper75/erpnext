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
