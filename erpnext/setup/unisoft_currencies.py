# Copyright (c) 2026, Unisoft and Contributors
# License: GNU General Public License v3. See license.txt

"""Restrict ERPNext to EGP, USD, and SAR only."""

from __future__ import annotations

import frappe

ALLOWED_CURRENCIES = ("EGP", "USD", "SAR")

CURRENCY_DEFAULTS = {
	"EGP": {
		"currency_name": "EGP",
		"enabled": 1,
		"fraction": "Piastre",
		"fraction_units": 100,
		"symbol": "E£",
		"number_format": "#,###.##",
	},
	"USD": {
		"currency_name": "USD",
		"enabled": 1,
		"fraction": "Cent",
		"fraction_units": 100,
		"symbol": "$",
		"number_format": "#,###.##",
	},
	"SAR": {
		"currency_name": "SAR",
		"enabled": 1,
		"fraction": "Halala",
		"fraction_units": 100,
		"symbol": "﷼",
		"number_format": "#,###.##",
	},
}


def ensure_allowed_currencies() -> None:
	"""Create/enable EGP, USD, SAR."""
	for code, values in CURRENCY_DEFAULTS.items():
		if frappe.db.exists("Currency", code):
			frappe.db.set_value("Currency", code, "enabled", 1, update_modified=False)
			for field, value in values.items():
				if field in ("currency_name", "enabled"):
					continue
				current = frappe.db.get_value("Currency", code, field)
				if current in (None, ""):
					frappe.db.set_value("Currency", code, field, value, update_modified=False)
		else:
			doc = frappe.get_doc({"doctype": "Currency", **values})
			doc.flags.ignore_permissions = True
			doc.insert()


def disable_other_currencies() -> int:
	"""Disable every currency except the allowed set."""
	frappe.db.sql(
		"""
		UPDATE `tabCurrency`
		SET enabled = 0
		WHERE name NOT IN %(allowed)s
		""",
		{"allowed": ALLOWED_CURRENCIES},
	)
	return frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabCurrency`
		WHERE enabled = 0 AND name NOT IN %(allowed)s
		""",
		{"allowed": ALLOWED_CURRENCIES},
	)[0][0]


def delete_unused_other_currencies() -> int:
	"""Delete non-allowed currencies when nothing references them."""
	deleted = 0
	others = frappe.get_all(
		"Currency",
		filters={"name": ("not in", list(ALLOWED_CURRENCIES))},
		pluck="name",
	)
	for name in others:
		try:
			frappe.delete_doc("Currency", name, force=1, ignore_permissions=True)
			frappe.db.commit()
			deleted += 1
		except Exception:
			frappe.db.rollback()
			frappe.db.set_value("Currency", name, "enabled", 0, update_modified=False)
			frappe.db.commit()
	return deleted


def cleanup_pegged_currencies() -> None:
	"""Keep only pegged rows that use allowed currencies."""
	if not frappe.db.exists("DocType", "Pegged Currencies"):
		return
	if not frappe.db.exists("Pegged Currencies", "Pegged Currencies"):
		return

	doc = frappe.get_single("Pegged Currencies")
	kept = []
	for row in doc.pegged_currency_item:
		if row.source_currency in ALLOWED_CURRENCIES and row.pegged_against in ALLOWED_CURRENCIES:
			kept.append(row.as_dict())
	doc.set("pegged_currency_item", [])
	for row in kept:
		doc.append(
			"pegged_currency_item",
			{
				"source_currency": row.get("source_currency"),
				"pegged_against": row.get("pegged_against"),
				"pegged_exchange_rate": row.get("pegged_exchange_rate"),
			},
		)
	# Ensure SAR -> USD peg remains (standard GCC peg)
	sources = {r.source_currency for r in doc.pegged_currency_item}
	if "SAR" not in sources and frappe.db.exists("Currency", "SAR") and frappe.db.exists("Currency", "USD"):
		doc.append(
			"pegged_currency_item",
			{"source_currency": "SAR", "pegged_against": "USD", "pegged_exchange_rate": 3.75},
		)
	doc.flags.ignore_permissions = True
	doc.save()


def restrict_currencies(delete_unused: bool = True) -> dict:
	"""Apply Unisoft currency policy: only EGP, USD, SAR available in the system."""
	ensure_allowed_currencies()
	disabled = disable_other_currencies()
	deleted = delete_unused_other_currencies() if delete_unused else 0
	cleanup_pegged_currencies()
	frappe.clear_cache()
	frappe.db.commit()
	enabled = frappe.get_all("Currency", filters={"enabled": 1}, pluck="name", order_by="name")
	remaining = frappe.get_all("Currency", pluck="name", order_by="name")
	return {
		"allowed": list(ALLOWED_CURRENCIES),
		"enabled": enabled,
		"remaining": remaining,
		"disabled_count": disabled,
		"deleted_count": deleted,
	}


def execute():
	"""Callable via bench execute / patches."""
	result = restrict_currencies(delete_unused=True)
	print(f"UNISOFT_CURRENCIES={result}")
	return result
