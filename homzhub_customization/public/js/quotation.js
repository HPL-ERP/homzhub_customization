frappe.ui.form.on('Quotation', {
	refresh: function(frm) {
		frm.add_custom_button('Journal Entry', () => {

		frappe.model.open_mapped_doc({
			method: "homzhub_customization.homzhub_customization.doctype.quotation.make_journal_entry",
			frm: me.frm
		})

		},
		__('Create')
		)	

	},
	validate: function(frm){
		frm.set_value('amount',frm.doc.total)
	},
	setup:function(frm){
		frm.set_query('property_address', function(doc) {
			return {
				query: 'homzhub_customization.homzhub_customization.doctype.project.address_query',
				filters: {
					link_doctype: 'Customer',
					link_name:[frm.doc.party_name]
				}
			};
		});
	},
	property_address: function(frm){
		frm.set_value('property_address_details', "");
		if (frm.doc.property_address!=undefined){
		frappe.call({
			method: "frappe.contacts.doctype.address.address.get_address_display",
			args: {"address_dict": frm.doc.property_address},
			callback: function(r) {
				if(r.message) {
					frm.set_value('property_address_details', r.message);
				}
			}
		});
	}
}
})