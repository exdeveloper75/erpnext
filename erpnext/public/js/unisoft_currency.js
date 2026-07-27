// Limit Currency link fields to EGP, USD, SAR only.
frappe.ready(function () {
	const allowed = ["EGP", "USD", "SAR"];

	function applyCurrencyQuery(frm) {
		if (!frm || !frm.meta) return;
		(frm.meta.fields || []).forEach((df) => {
			if (df.fieldtype === "Link" && df.options === "Currency") {
				frm.set_query(df.fieldname, () => ({
					filters: {
						enabled: 1,
						name: ["in", allowed],
					},
				}));
			}
		});
		(frm.meta.fields || []).forEach((df) => {
			if (df.fieldtype === "Table" && frm.fields_dict[df.fieldname]) {
				const grid = frm.fields_dict[df.fieldname].grid;
				if (!grid || !grid.docfields) return;
				grid.docfields.forEach((cdf) => {
					if (cdf.fieldtype === "Link" && cdf.options === "Currency") {
						grid.get_field(cdf.fieldname).get_query = () => ({
							filters: {
								enabled: 1,
								name: ["in", allowed],
							},
						});
					}
				});
			}
		});
	}

	$(document).on("form-load", function (_e, frm) {
		applyCurrencyQuery(frm);
	});

	// Currency list: prefer enabled only
	frappe.listview_settings["Currency"] = frappe.listview_settings["Currency"] || {};
	const prev = frappe.listview_settings["Currency"].onload;
	frappe.listview_settings["Currency"].onload = function (listview) {
		if (prev) prev(listview);
		listview.filter_area.add([["Currency", "enabled", "=", 1]]);
	};
});
