# Copyright (c) 2026, MezanErp and Contributors
# License: GNU General Public License v3. See license.txt

import frappe

APP_DISPLAY_NAME = "Mezan ERP"
APP_LOGO = "/assets/erpnext/images/mezan-logo.svg"
APP_FAVICON = "/assets/erpnext/images/mezan-favicon.svg"


def set_app_display_name():
	"""Set System + Website branding to Mezan ERP with M logo."""
	frappe.db.set_single_value("System Settings", "app_name", APP_DISPLAY_NAME)

	ws = frappe.get_single("Website Settings")
	if hasattr(ws, "app_name"):
		ws.app_name = APP_DISPLAY_NAME
	if hasattr(ws, "title_prefix"):
		ws.title_prefix = APP_DISPLAY_NAME
	if hasattr(ws, "brand_html"):
		ws.brand_html = (
			f'<img src="{APP_LOGO}" alt="{APP_DISPLAY_NAME}" '
			f'style="height:28px;width:28px;border-radius:6px;vertical-align:middle;margin-right:8px;">'
			f"<b>{APP_DISPLAY_NAME}</b>"
		)
	if hasattr(ws, "favicon"):
		ws.favicon = APP_FAVICON
	if hasattr(ws, "splash_image"):
		ws.splash_image = APP_LOGO
	if hasattr(ws, "banner_image"):
		# keep empty unless site has custom banner
		pass
	ws.flags.ignore_permissions = True
	ws.save()

	# Desk / navbar app logo used by boot
	try:
		frappe.db.set_single_value("Navbar Settings", "app_logo", APP_LOGO)
	except Exception:
		pass

	frappe.clear_cache()
	frappe.db.commit()
	return APP_DISPLAY_NAME


def execute():
	name = set_app_display_name()
	print(f"APP_NAME_SET={name}")
	return name
