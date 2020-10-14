cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Subscription',
			'Rent Transaction',
			'Journal Entry',
			'Lead',
			'Quotation'
		],
		'label': 'Others'
	},
]);
frappe.ui.form.on('Project', {
    setup(frm) {
		let customer = [];
		cur_frm.doc.owner_list.forEach(value => {
			customer.push(value.prop_owner)
		});
		// customer.push(frm.doc.property_owner)
		frm.set_query('property_address', function(doc) {
			return {
				query: 'homzhub_customization.homzhub_customization.doctype.project.address_query',
				filters: {
					link_doctype: 'Customer',
					link_name: customer
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
		frm.set_query("employee", "participant_list", function() {
			return {
				filters: {
					status:'Active'
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
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.project.fetch_inventory_table",
			args: {
				address: frm.doc.property_address,
			},
			callback: function (data) {
				if (data.message){
					$.each(data.message, function (i, v) {
						var d = cur_frm.add_child("inventory_list")
						d.asset = v.asset
						d.quantity=v.quantity
						d.description=v.description
					})
					cur_frm.refresh_field("inventory_list")
				}	
			}
		})
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
	project_type:function(frm){
		frm.set_value('cost_center',"")
		if (frm.doc.project_type=="Property Selling"){
			frm.set_value('cost_center',"Property Selling - HAPL")
		}
	},
	default_designation:function(frm){
		if(frm.doc.default_designation){
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.project.fetch_participant_table",
			args: {
				designation: frm.doc.default_designation,
				table:frm.doc.participant_list || []
			},
			callback: function (data) {
				frm.clear_table("participant_list")
				if (data.message){
					$.each(data.message, function (i, v) {
						var d = cur_frm.add_child("participant_list")
						d.user=v.user_id
						d.employee=v.name
						d.employee_name=v.employee_name
						d.designation=v.designation
					})
					cur_frm.refresh_field("participant_list")
				}	
			}
		})
	}
	},
	default_department:function(frm){
		if(frm.doc.default_department){
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.project.fetch_department_participant_table",
			args: {
				department: frm.doc.default_department,
				table:frm.doc.participant_list || []
			},
			callback: function (data) {
				frm.clear_table("participant_list")
				if (data.message){
					$.each(data.message, function (i, v) {
						var d = cur_frm.add_child("participant_list")
						d.user=v.user_id
						d.employee=v.name
						d.employee_name=v.employee_name
						d.designation=v.designation
					})
					cur_frm.refresh_field("participant_list")
				}	
			}
		})
	}
	},
	sync_with_address:function(frm){
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.project.set_inventory_details",
			args: {
				doc: frm.doc
			},
			callback: function (data) {
				console.log('')
			}
		})
	}

})
frappe.ui.form.on("Tenant List", "tenant", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value('Customer', {name: d.tenant}, 'customer_name', (r) => {
		d.tenant_name = r.customer_name
		refresh_field("tenant_name", d.name, d.parentfield);
	})
	frappe.call({
		method:
		"homzhub_customization.homzhub_customization.doctype.project.get_contact_list",
		args: {
			tenant: d.tenant
		},
		callback: function (data) {
			if (data.message){
				$.each(data.message, function (i, v) {
					var contact = cur_frm.add_child("contacts_list")
					contact.contact=v.contact
					contact.first_name=v.first_name
					contact.middle_name=v.middle_name
					contact.last_name=v.last_name
				})
				cur_frm.refresh_field("contacts_list")
			}
		}
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
frappe.ui.form.on("Project Participants", "user", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value('Employee', {user_id: d.user}, ['name','employee_name','designation'], (r) => {
		d.employee=r.name
		d.employee_name=r.employee_name
		d.designation=r.designation
		refresh_field("employee", d.name, d.parentfield);
		refresh_field("employee_name", d.name, d.parentfield);
		refresh_field("designation", d.name, d.parentfield);
	})

});

frappe.ui.form.on("Owner List", "prop_owner", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.db.get_value('Customer', {name: d.prop_owner}, ['customer_name'], (r) => {
		d.owner_name=r.customer_name
		refresh_field("owner_name", d.name, d.parentfield);
	})

});