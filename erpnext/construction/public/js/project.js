frappe.ui.form.on("Project", {
	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(
			__("Project Budget"),
			() => open_or_create_budget(frm),
			__("Construction")
		);
		frm.add_custom_button(
			__("Labor Costs"),
			() => {
				frappe.set_route("List", "Construction Labor Cost", { project: frm.doc.name });
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Equipment Costs"),
			() => {
				frappe.set_route("List", "Construction Equipment Cost", { project: frm.doc.name });
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Contracts"),
			() => {
				frappe.set_route("List", "Construction Contract", { project: frm.doc.name });
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Customer Certificates"),
			() => {
				frappe.set_route("List", "Customer Payment Certificate", { project: frm.doc.name });
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Contractor Certificates"),
			() => {
				frappe.set_route("List", "Contractor Payment Certificate", { project: frm.doc.name });
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Change Orders"),
			() => {
				frappe.set_route("List", "Change Order", { project: frm.doc.name });
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Construction P&L"),
			() => {
				frappe.set_route("query-report", "Project Construction P and L", {
					company: frm.doc.company,
					project: frm.doc.name,
				});
			},
			__("Construction")
		);
	},
});

function open_or_create_budget(frm) {
	frappe.db.get_value(
		"Construction Project Budget",
		{ project: frm.doc.name, docstatus: ["<", 2] },
		"name",
		(r) => {
			if (r && r.name) {
				frappe.set_route("Form", "Construction Project Budget", r.name);
				return;
			}
			frappe.model.with_doctype("Construction Project Budget", () => {
				const doc = frappe.model.get_new_doc("Construction Project Budget");
				doc.project = frm.doc.name;
				doc.company = frm.doc.company;
				doc.title = frm.doc.project_name || frm.doc.name;
				doc.items = [];
				["Materials", "Labor", "Equipment", "Subcontract", "Expenses"].forEach((cat) => {
					const row = frappe.model.add_child(doc, "items");
					row.cost_category = cat;
					row.budget_amount = 0;
				});
				frappe.set_route("Form", "Construction Project Budget", doc.name);
			});
		}
	);
}
