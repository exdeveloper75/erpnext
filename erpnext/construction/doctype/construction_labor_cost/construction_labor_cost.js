frappe.ui.form.on("Construction Labor Cost", {
	hours(frm) {
		frm.set_value("amount", flt(frm.doc.hours) * flt(frm.doc.rate));
	},
	rate(frm) {
		frm.set_value("amount", flt(frm.doc.hours) * flt(frm.doc.rate));
	},
	project(frm) {
		if (!frm.doc.project) return;
		frappe.db.get_value("Project", frm.doc.project, "company", (r) => {
			if (r) frm.set_value("company", r);
		});
	},
});
