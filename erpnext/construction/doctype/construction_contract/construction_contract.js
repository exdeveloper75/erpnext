frappe.ui.form.on("Construction Contract", {
	contract_type(frm) {
		frm.set_value(
			"party_type",
			frm.doc.contract_type === "Contractor" ? "Supplier" : "Customer"
		);
		frm.set_value("party", "");
	},
	items_add(frm) {
		frm.trigger("calculate_totals");
	},
	calculate_totals(frm) {
		let total = 0;
		(frm.doc.items || []).forEach((row) => {
			row.amount = flt(row.qty) * flt(row.rate);
			total += flt(row.amount);
		});
		frm.set_value("total_amount", total);
		frm.refresh_field("items");
	},
});

frappe.ui.form.on("Construction Contract Item", {
	qty(frm, cdt, cdn) {
		calculate_row(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_row(frm, cdt, cdn);
	},
});

function calculate_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
	frm.trigger("calculate_totals");
}
