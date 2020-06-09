cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Subscription'
		],
		'label': 'Others'
	},
]);
frappe.ui.form.on('Project', {
    setup(frm) {
		frm.set_query('property_address', function(doc) {
			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: 'Customer',
					link_name: doc.property_owner
				}
			};
		});
    },
    property_owner: function(frm){
		frm.set_value('property_address','');
	},
	property_address: function(frm){
		if (frm.doc.property_address!=undefined){
		frappe.call({
			method: "frappe.contacts.doctype.address.address.get_address_display",
			args: {"address_dict": frm.doc.property_address},
			callback: function(r) {
				if(r.message) {
					frm.set_value('address_detail', r.message);
				}
			}
		});
	}
	},
	fixed_rent:function(frm){
		if (frm.doc.fixed_rent==1){
			frm.set_value('varying_rent',0)
			}
		else{
			frm.set_value('fixed_rent',0)
			frm.set_value('varying_rent',1)
		}
	},
	varying_rent:function(frm){
		if (frm.doc.varying_rent==1){
			frm.set_value('fixed_rent',0)
			}
		else{
			frm.set_value('fixed_rent',1)
			frm.set_value('varying_rent',0)
		}
	},
})