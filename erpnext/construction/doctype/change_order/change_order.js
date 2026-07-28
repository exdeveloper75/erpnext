frappe.ui.form.on("Change Order", {
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

frappe.ui.form.on("Change Order Item", {
	qty(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
		frm.trigger("calculate_totals");
	},
	rate(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
		frm.trigger("calculate_totals");
	},
});
