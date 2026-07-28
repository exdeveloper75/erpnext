# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Project": [
				{
					"fieldname": "construction_section",
					"fieldtype": "Section Break",
					"label": "Construction",
					"insert_after": "department",
					"collapsible": 1,
				},
				{
					"fieldname": "primary_construction_contract",
					"fieldtype": "Link",
					"label": "Primary Construction Contract",
					"options": "Construction Contract",
					"insert_after": "construction_section",
				},
				{
					"fieldname": "site_location",
					"fieldtype": "Small Text",
					"label": "Site Location",
					"insert_after": "primary_construction_contract",
				},
				{
					"fieldname": "column_break_construction_1",
					"fieldtype": "Column Break",
					"insert_after": "site_location",
				},
				{
					"fieldname": "client_representative",
					"fieldtype": "Data",
					"label": "Client Representative",
					"insert_after": "column_break_construction_1",
				},
				{
					"fieldname": "site_engineer",
					"fieldtype": "Data",
					"label": "Site Engineer",
					"insert_after": "client_representative",
				},
				{
					"fieldname": "construction_percents_section",
					"fieldtype": "Section Break",
					"label": "Construction Contract Defaults",
					"insert_after": "site_engineer",
					"collapsible": 1,
				},
				{
					"fieldname": "construction_retention_percent",
					"fieldtype": "Percent",
					"label": "Retention %",
					"insert_after": "construction_percents_section",
					"default": "0",
				},
				{
					"fieldname": "construction_advance_percent",
					"fieldtype": "Percent",
					"label": "Advance %",
					"insert_after": "construction_retention_percent",
					"default": "0",
				},
				{
					"fieldname": "column_break_construction_2",
					"fieldtype": "Column Break",
					"insert_after": "construction_advance_percent",
				},
				{
					"fieldname": "construction_delay_penalty_percent",
					"fieldtype": "Percent",
					"label": "Delay Penalty %",
					"insert_after": "column_break_construction_2",
					"default": "0",
				},
			]
		},
		update=True,
	)
	frappe.clear_cache(doctype="Project")
