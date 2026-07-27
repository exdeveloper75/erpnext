# Copyright (c) 2026, MezanErp and Contributors
# License: GNU General Public License v3. See license.txt

import frappe

APP_DISPLAY_NAME = "MezanErp"


def set_app_display_name():
	"""Set System + Website branding to MezanErp."""
	frappe.db.set_single_value("System Settings", "app_name", APP_DISPLAY_NAME)

	ws = frappe.get_single("Website Settings")
	if hasattr(ws, "app_name"):
		ws.app_name = APP_DISPLAY_NAME
	if hasattr(ws, "title_prefix"):
		ws.title_prefix = APP_DISPLAY_NAME
	if hasattr(ws, "brand_html"):
		ws.brand_html = f"<b>{APP_DISPLAY_NAME}</b>"
	ws.flags.ignore_permissions = True
	ws.save()

	frappe.clear_cache()
	frappe.db.commit()
	return APP_DISPLAY_NAME


def execute():
	name = set_app_display_name()
	print(f"APP_NAME_SET={name}")
	return name
