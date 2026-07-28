# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe

WORKFLOW_STATES = [
	("Draft", "Primary"),
	("Pending Review", "Warning"),
	("Pending Approval", "Warning"),
	("Approved", "Success"),
	("Rejected", "Danger"),
]

WORKFLOW_ACTIONS = [
	"Send for Review",
	"Recommend",
	"Approve",
	"Reject",
]

DOCTYPES = [
	{
		"doctype": "Construction Contract",
		"workflow_name": "Construction Contract Approval",
		"approved_status": "Active",
		"rejected_status": "Draft",
	},
	{
		"doctype": "Change Order",
		"workflow_name": "Change Order Approval",
		"approved_status": "Approved",
		"rejected_status": "Rejected",
	},
	{
		"doctype": "Customer Payment Certificate",
		"workflow_name": "Customer Payment Certificate Approval",
		"approved_status": "Approved",
		"rejected_status": "Draft",
	},
	{
		"doctype": "Contractor Payment Certificate",
		"workflow_name": "Contractor Payment Certificate Approval",
		"approved_status": "Approved",
		"rejected_status": "Draft",
	},
]

REVIEW_ROLES = ("Projects User", "Projects Manager", "System Manager")
APPROVE_ROLES = ("Projects Manager", "System Manager")


def execute():
	ensure_states()
	ensure_actions()
	for cfg in DOCTYPES:
		ensure_workflow(cfg)


def ensure_states():
	for state, style in WORKFLOW_STATES:
		if frappe.db.exists("Workflow State", state):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Workflow State",
				"workflow_state_name": state,
				"style": style,
			}
		)
		doc.insert(ignore_permissions=True)


def ensure_actions():
	for action in WORKFLOW_ACTIONS:
		if frappe.db.exists("Workflow Action Master", action):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Workflow Action Master",
				"workflow_action_name": action,
			}
		)
		doc.insert(ignore_permissions=True)


def ensure_workflow(cfg):
	name = cfg["workflow_name"]
	if frappe.db.exists("Workflow", name):
		# Keep existing definition if already created (idempotent).
		return

	states = [
		{
			"state": "Draft",
			"doc_status": "0",
			"allow_edit": "Projects User",
			"is_optional_state": 0,
		},
		{
			"state": "Pending Review",
			"doc_status": "0",
			"allow_edit": "Projects User",
			"is_optional_state": 0,
		},
		{
			"state": "Pending Approval",
			"doc_status": "0",
			"allow_edit": "Projects Manager",
			"is_optional_state": 0,
		},
		{
			"state": "Approved",
			"doc_status": "1",
			"allow_edit": "System Manager",
			"is_optional_state": 0,
			"update_field": "status",
			"update_value": cfg["approved_status"],
		},
		{
			"state": "Rejected",
			"doc_status": "0",
			"allow_edit": "Projects Manager",
			"is_optional_state": 1,
			"update_field": "status",
			"update_value": cfg["rejected_status"],
		},
	]

	transitions = []
	for role in REVIEW_ROLES:
		transitions.append(
			{
				"state": "Draft",
				"action": "Send for Review",
				"next_state": "Pending Review",
				"allowed": role,
				"allow_self_approval": 1,
			}
		)
		transitions.append(
			{
				"state": "Pending Review",
				"action": "Recommend",
				"next_state": "Pending Approval",
				"allowed": role,
				"allow_self_approval": 1,
			}
		)
		transitions.append(
			{
				"state": "Rejected",
				"action": "Send for Review",
				"next_state": "Pending Review",
				"allowed": role,
				"allow_self_approval": 1,
			}
		)

	for role in APPROVE_ROLES:
		transitions.append(
			{
				"state": "Pending Approval",
				"action": "Approve",
				"next_state": "Approved",
				"allowed": role,
				"allow_self_approval": 1,
			}
		)
		for from_state in ("Pending Review", "Pending Approval"):
			transitions.append(
				{
					"state": from_state,
					"action": "Reject",
					"next_state": "Rejected",
					"allowed": role,
					"allow_self_approval": 1,
				}
			)

	doc = frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": name,
			"document_type": cfg["doctype"],
			"is_active": 1,
			"override_status": 1,
			"send_email_alert": 0,
			"workflow_state_field": "workflow_state",
			"states": states,
			"transitions": transitions,
		}
	)
	doc.insert(ignore_permissions=True)
