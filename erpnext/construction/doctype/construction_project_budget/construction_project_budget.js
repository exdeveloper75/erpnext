frappe.ui.form.on("Construction Project Budget", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Refresh Actuals"), () => {
				frappe.call({
					method: "refresh_actuals",
					doc: frm.doc,
					freeze: true,
					freeze_message: __("Refreshing actuals…"),
					callback(r) {
						frm.reload_doc();
						if (r.message) {
							frappe.show_alert({
								message: __("Actuals updated. Estimated profit: {0}", [
									format_currency(r.message.estimated_profit, frm.doc.currency),
								]),
								indicator: "green",
							});
						}
					},
				});
			});
		}
		if (frm.doc.project) {
			frm.add_custom_button(__("Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.project);
			});
		}
		if (frm.doc.construction_contract) {
			frm.add_custom_button(__("Contract"), () => {
				frappe.set_route("Form", "Construction Contract", frm.doc.construction_contract);
			});
		}
	},
	project(frm) {
		if (!frm.doc.project) return;
		frappe.db.get_value("Project", frm.doc.project, ["project_name", "company"], (r) => {
			if (!r) return;
			if (!frm.doc.title) frm.set_value("title", r.project_name || frm.doc.project);
			if (!frm.doc.company) frm.set_value("company", r.company);
		});
		frappe.db.get_value(
			"Construction Contract",
			{ project: frm.doc.project, docstatus: 1, contract_type: "Customer" },
			["name", "currency", "contract_value"],
			(r) => {
				if (!r) return;
				frm.set_value("construction_contract", r.name);
				if (r.currency) frm.set_value("currency", r.currency);
			}
		);
	},
	items_add(frm) {
		frm.trigger("recalc_client");
	},
	recalc_client(frm) {
		let budget = 0;
		(frm.doc.items || []).forEach((row) => {
			row.variance = flt(row.budget_amount) - flt(row.actual_amount);
			budget += flt(row.budget_amount);
		});
		frm.set_value("total_budget", budget);
		frm.refresh_field("items");
	},
});

frappe.ui.form.on("Construction Project Budget Item", {
	budget_amount(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "variance", flt(row.budget_amount) - flt(row.actual_amount));
		frm.trigger("recalc_client");
	},
});
