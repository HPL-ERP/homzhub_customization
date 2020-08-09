cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Subscription',
			'Rent Transaction',
			'Journal Entry',
			'Lead'
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
		frm.set_query("tenant", "tenant_list", function() {
			return {
				filters: {
					customer_group:'Tenant'
				}
			}
		});
    },
    property_owner: function(frm){
		frm.set_value('property_address','');
		frm.set_value("owner_name","")
		frappe.db.get_value("Customer", {"name":cur_frm.doc.property_owner},"customer_name", function(r){
			frm.set_value("owner_name",r.customer_name)
			})
	},
	property_tenant: function(frm){
		frm.set_value("tenant_name","")
		frappe.db.get_value("Customer", {"name":frm.doc.property_tenant},"customer_name", function(r){
        frm.set_value("tenant_name",r.customer_name)
		})
	},
	property_address: function(frm){
		frm.set_value('address_detail', "");
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
	agreement_start_date:function(frm){
		frm.set_value('lock_in_period_start',frm.doc.agreement_start_date)
	},
	// main_buyer:function(frm){
	// 	frappe.db.get_value('Lead', {name: frm.doc.main_buyer}, ['lead_name','company_name'], (r) => {
	// 		if(r.lead_name){
	// 		frm.set_value('main_buyer_name',r.lead_name)
	// 		}
	// 		else{
	// 			frm.set_value('main_buyer_name',r.company_name)
	// 		}
		
	// })
	// }

})
frappe.ui.form.on("Tenant List", "tenant", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value('Customer', {name: d.tenant}, 'customer_name', (r) => {
		d.tenant_name = r.customer_name
		refresh_field("tenant_name", d.name, d.parentfield);
	})

});
frappe.ui.form.on("Buyer List", "buyer", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value('Lead', {name: d.buyer}, ['lead_name','company_name'], (r) => {
		if(r.lead_name){
			d.buyer_name = r.lead_name
		}
		else{
			d.buyer_name = r.company_name
		}
		refresh_field("buyer_name", d.name, d.parentfield);
	})

});

frappe.ui.form.on("Buyer List", "buyer", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value('Lead', {name: d.buyer}, ['lead_name','company_name'], (r) => {
		if(r.lead_name){
			d.buyer_name = r.lead_name
		}
		else{
			d.buyer_name = r.company_name
		}
		refresh_field("buyer_name", d.name, d.parentfield);
	})

});
