# Copyright (c) 2026, MezanErp and Contributors
# License: GNU General Public License v3. See license.txt

"""Ensure Arabic language is available for MezanErp."""

from __future__ import annotations

import frappe

ARABIC_CODE = "ar"
ARABIC_NAME = "العربية"


def ensure_arabic_language() -> dict:
	"""Enable Arabic language and set sensible defaults."""
	if frappe.db.exists("Language", ARABIC_CODE):
		frappe.db.set_value(
			"Language",
			ARABIC_CODE,
			{
				"enabled": 1,
				"language_name": ARABIC_NAME,
				"language_code": ARABIC_CODE,
				"date_format": "dd-mm-yyyy",
				"time_format": "HH:mm:ss",
			},
			update_modified=False,
		)
	else:
		doc = frappe.get_doc(
			{
				"doctype": "Language",
				"language_code": ARABIC_CODE,
				"language_name": ARABIC_NAME,
				"enabled": 1,
				"date_format": "dd-mm-yyyy",
				"time_format": "HH:mm:ss",
			}
		)
		doc.flags.ignore_permissions = True
		doc.insert()

	# Keep English enabled as well
	if frappe.db.exists("Language", "en"):
		frappe.db.set_value("Language", "en", "enabled", 1, update_modified=False)

	frappe.clear_cache()
	frappe.db.commit()

	enabled = frappe.get_all(
		"Language",
		filters={"enabled": 1},
		fields=["name", "language_name"],
		order_by="name",
	)
	return {
		"arabic_enabled": True,
		"arabic_code": ARABIC_CODE,
		"enabled_languages": enabled,
	}


def execute():
	result = ensure_arabic_language()
	print(f"ARABIC_LANGUAGE={result}")
	return result
