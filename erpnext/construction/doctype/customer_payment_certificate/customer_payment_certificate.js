frappe.ui.form.on("Customer Payment Certificate", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.construction_contract) {
			frm.add_custom_button(__("Get Items from Contract"), () => {
				frappe.call({
					method: "get_items_from_contract",
					doc: frm.doc,
					freeze: true,
					callback(r) {
						frm.refresh_fields();
						frappe.show_alert({
							message: __("Loaded {0} BOQ line(s)", [r.message || 0]),
							indicator: "green",
						});
					},
				});
			});
		}
		if (frm.doc.docstatus === 1 && frm.doc.status === "Submitted") {
			frm.add_custom_button(__("Mark Approved"), () => {
				frappe.call({
					method: "mark_approved",
					doc: frm.doc,
					freeze: true,
					callback() {
						frm.reload_doc();
					},
				});
			});
		}
		if (frm.doc.docstatus === 1 && !frm.doc.sales_invoice) {
			frm.add_custom_button(__("Create Sales Invoice"), () => {
				frappe.call({
					method: "create_sales_invoice",
					doc: frm.doc,
					freeze: true,
					callback(r) {
						if (r.message) {
							frm.reload_doc();
							frappe.set_route("Form", "Sales Invoice", r.message);
						}
					},
				});
			});
		}
		if (frm.doc.sales_invoice) {
			frm.add_custom_button(__("Sales Invoice"), () => {
				frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice);
			});
		}
	},
	construction_contract(frm) {
		frm.trigger("calculate_totals");
	},
	project(frm) {
		frm.trigger("calculate_totals");
	},
	retention_percent(frm) {
		frm.trigger("calculate_totals");
	},
	advance_recovery(frm) {
		frm.trigger("calculate_totals");
	},
	retention_release(frm) {
		frm.trigger("calculate_totals");
	},
	calculate_totals(frm) {
		let gross = 0;
		(frm.doc.items || []).forEach((row) => {
			row.cumulative_qty = flt(row.previous_qty) + flt(row.current_qty);
			row.current_amount = flt(row.current_qty) * flt(row.rate);
			gross += flt(row.current_amount);
		});
		const retention = (gross * flt(frm.doc.retention_percent)) / 100;
		const claimed =
			gross - retention - flt(frm.doc.advance_recovery) + flt(frm.doc.retention_release);
		frm.set_value("gross_amount", gross);
		frm.set_value("retention_amount", retention);
		frm.set_value("claimed_amount", claimed);
		if (!flt(frm.doc.approved_amount)) {
			frm.set_value("approved_amount", claimed);
		}
		frm.refresh_field("items");
	},
});

frappe.ui.form.on("Payment Certificate Item", {
	previous_qty(frm, cdt, cdn) {
		recalc_pc_row(frm, cdt, cdn);
	},
	current_qty(frm, cdt, cdn) {
		recalc_pc_row(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		recalc_pc_row(frm, cdt, cdn);
	},
});

function recalc_pc_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "cumulative_qty", flt(row.previous_qty) + flt(row.current_qty));
	frappe.model.set_value(cdt, cdn, "current_amount", flt(row.current_qty) * flt(row.rate));
	frm.trigger("calculate_totals");
}
