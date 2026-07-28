frappe.ui.form.on("Construction Contract", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && !frm.doc.project && frm.doc.contract_type === "Customer") {
			frm.add_custom_button(__("Create Project"), () => {
				frappe.call({
					method: "create_project",
					doc: frm.doc,
					freeze: true,
					callback(r) {
						if (r.message) {
							frm.reload_doc();
							frappe.set_route("Form", "Project", r.message);
						}
					},
				});
			}).addClass("btn-primary");
		}
		if (frm.doc.project) {
			frm.add_custom_button(__("Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.project);
			});
		}
	},
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
