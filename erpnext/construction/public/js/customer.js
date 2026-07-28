frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(
			__("Contracts"),
			() => {
				frappe.set_route("List", "Construction Contract", {
					party: frm.doc.name,
					contract_type: "Customer",
				});
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Payment Certificates"),
			() => {
				frappe.set_route("List", "Customer Payment Certificate", {
					customer: frm.doc.name,
				});
			},
			__("Construction")
		);
		frm.add_custom_button(
			__("Construction Summary"),
			() => {
				frappe.set_route("query-report", "Customer Construction Summary", {
					customer: frm.doc.name,
				});
			},
			__("Construction")
		);
	},
});
