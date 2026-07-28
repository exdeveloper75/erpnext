frappe.ui.form.on("Contractor Payment Certificate", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && !frm.doc.purchase_invoice) {
			frm.add_custom_button(__("Create Purchase Invoice"), () => {
				frappe.call({
					method: "create_purchase_invoice",
					doc: frm.doc,
					freeze: true,
					callback(r) {
						if (r.message) {
							frm.reload_doc();
							frappe.set_route("Form", "Purchase Invoice", r.message);
						}
					},
				});
			});
		}
		if (frm.doc.purchase_invoice) {
			frm.add_custom_button(__("Purchase Invoice"), () => {
				frappe.set_route("Form", "Purchase Invoice", frm.doc.purchase_invoice);
			});
		}
	},
	retention_percent(frm) {
		frm.trigger("calculate_totals");
	},
	advance_recovery(frm) {
		frm.trigger("calculate_totals");
	},
	calculate_totals(frm) {
		let gross = 0;
		(frm.doc.items || []).forEach((row) => {
			row.cumulative_qty = flt(row.previous_qty) + flt(row.current_qty);
			row.current_amount = flt(row.current_qty) * flt(row.rate);
			gross += flt(row.current_amount);
		});
		frm.set_value("gross_amount", gross);
		frm.set_value("retention_amount", (gross * flt(frm.doc.retention_percent)) / 100);
		frm.set_value(
			"net_amount",
			gross - flt(frm.doc.retention_amount) - flt(frm.doc.advance_recovery)
		);
		frm.refresh_field("items");
	},
});

frappe.ui.form.on("Payment Certificate Item", {
	previous_qty(frm, cdt, cdn) {
		recalc_tpc_row(frm, cdt, cdn);
	},
	current_qty(frm, cdt, cdn) {
		recalc_tpc_row(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		recalc_tpc_row(frm, cdt, cdn);
	},
});

function recalc_tpc_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "cumulative_qty", flt(row.previous_qty) + flt(row.current_qty));
	frappe.model.set_value(cdt, cdn, "current_amount", flt(row.current_qty) * flt(row.rate));
	frm.trigger("calculate_totals");
}
