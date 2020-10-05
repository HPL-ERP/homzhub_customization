frappe.listview_settings['Sales Order'] = {
	add_fields: [ "status"],
	get_indicator: function (doc) {
	if (doc.status === "Invoiced") {
			return [__("Invoiced"), "green", "status,=,Inoiced"];
		}
	},
};
