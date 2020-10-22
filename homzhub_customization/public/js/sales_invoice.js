frappe.ui.form.on('Sales Invoice Item', {
    item_code:function(frm,cdt, cdn){
        var row = locals[cdt][cdn]
        frappe.db.get_value("Item", {"name":row.item_code},"service_charges_in_per", function(r){
        row.service_charges_in_per=r.service_charges_in_per
		})
    },
})

frappe.ui.form.on('Sales Invoice', {
validate:function(frm){
	if (!frm.doc.project){
		frappe.call({
			method: "homzhub_customization.homzhub_customization.doctype.sales_invoice.get_customer_list",
			args: {"customer": frm.doc.customer},
			callback: function(r) {
				if(r.message) {
					frappe.confirm(
						"Customer available in this project <b>"+r.message+"</b> </br>And do you want to link this invoice?",
									function(){
										frm.set_value('project',r.message)
									},
									function(){
										frappe.confirm(
											'Do you want new project?',
											function(){
												let table_values1 = [];
												let table_values2 = [];
												var d = new frappe.ui.Dialog({
													title: __("New Project"),
													fields: [
														{
															'fieldname': 'project_name',
															'fieldtype': 'Data',
															'label': __('Project Name'),
															'reqd': 1
														},
														{
															'fieldname': 'project_template',
															'fieldtype': 'Link',
															'label': __('From Template'),
															'options': 'Project Template'
														},
														{
															'fieldname': 'expected_start_date',
															'fieldtype': 'Date',
															'label': __('Expected Start Date')
														},
														{
															'fieldname': 'expected_end_date',
															'fieldtype': 'Date',
															'label': __('Expected End Date')
														},
														{
															'fieldname': 'project_type',
															'fieldtype': 'Link',
															'label': __('Project Type'),
															'options':'Project Type'
														},
														{
															'fieldname': 'owner_list',
															'fieldtype': 'Table',
															'label': __('Owner List'),
															'options':'Owner List',
															'fields':[
																{
																	fieldtype:'Link',
																	fieldname:'prop_owner',
																	label: __('Owner'),
																	options:'Customer',
																	in_list_view:1,
																	onchange: function() {
																		Object.values(table_values1).forEach(i=>{
																			frappe.db.get_value('Customer', {name: i.prop_owner}, ['customer_name'], (r) => {
																				i['owner_name']=r.customer_name
																				d.fields_dict.owner_list.grid.refresh();
																			})
																			})
																			d.fields_dict.owner_list.grid.refresh();
																	}
																},
																{
																	fieldtype:'Data',
																	fieldname:'owner_name',
																	label: __('Owner Name'),
																	in_list_view:1
																}
															],
															data: table_values1,
															in_place_edit: true,
															get_data: function() {
																return table_values1;
															}
														},
														{
															'fieldname': 'tenant_list',
															'fieldtype': 'Table',
															'label': __('Tenant List'),
															'options':'Tenant List',
															'fields':[
																{
																	fieldtype:'Link',
																	fieldname:'tenant',
																	label: __('Tenant'),
																	options:'Customer',
																	in_list_view:1,
																	onchange: function() {
																		Object.values(table_values2).forEach(i=>{
																			frappe.db.get_value('Customer', {name: i.tenant}, ['customer_name'], (r) => {
																				i['tenant_name']=r.customer_name
																				d.fields_dict.tenant_list.grid.refresh();
																			})
																			})
																			d.fields_dict.tenant_list.grid.refresh();
																	}
																},
																{
																	fieldtype:'Data',
																	fieldname:'tenant_name',
																	label: __('Tenant Name'),
																	in_list_view:1
																}
															],
															data: table_values2,
															in_place_edit: true,
															get_data: function() {
																return table_values2;
															}
														},
														{
															'fieldname': 'property_address',
															'fieldtype': 'Link',
															'label': __('Property Address'),
															'options':'Address',
															"get_query": function () {
															let customer = [];
															if (d.get_value('owner_list')){
															Object.values(d.get_value('owner_list')).forEach(function(value) {
																customer.push(value.prop_owner)
															});
															}
															return {
																query: 'homzhub_customization.homzhub_customization.doctype.project.address_query',
																filters: {
																	link_doctype: 'Customer',
																	link_name: customer
																}
															};
														}

														},
														
													],
													primary_action: function(){
														d.hide();
														frappe.call({
															args: {
																'doc':d.get_values()
															},
															method: "homzhub_customization.homzhub_customization.doctype.sales_invoice.make_project",
															callback: function (r) {
																if (r.message) {
																	frm.set_value('project',r.message)
																}
															}
														});
														},
														primary_action_label: __('Save')
												});
												d.show();
											},
											function(){
												window.close();
											}
										)
									}
								)
				}
			}
		});
	}
	frm.set_value('total_taxes_and_charges',Math.round(frm.doc.total_taxes_and_charges))
	if (frm.doc.is_selling_property_==1){
		cur_frm.doc.items.forEach(function(itm){
		itm.rate=(parseInt(itm.service_charges_in_per)/100*parseInt(frm.doc.property_rate))
	})
	}
	if (frm.doc.calculate_rate_from_property==1){
		cur_frm.doc.items.forEach(function(itm){
			console.log(parseInt(itm.service_charges_in_per)/100*parseInt(frm.doc.property_rent))
		itm.rate=(parseInt(itm.service_charges_in_per)/100*parseInt(frm.doc.property_rent)*11)
	})
	}
},
is_selling_property_:function(frm){
		if (frm.doc.is_selling_property_==1){
			 frappe.db.get_value("Project", {"name":frm.doc.project},"property_rate", function(r){
	      	 frm.set_value('property_rate',r.property_rate)
			})
		}
	else{
			frm.set_value('property_rate','')
		}

},
project:function(frm){
	frappe.db.get_value("Project", {"name":frm.doc.project},["property_address","address_detail","agreement_start_date","agreement_end_date","property_rent","agreement_tenure"], function(r){
	      	frm.set_value('property_address',r.property_address)
			frm.set_value('property_address_detail',r.address_detail)
			frm.set_value('agreement_start_date',r.agreement_start_date)
			frm.set_value('agreement_end_date',r.agreement_end_date)
			frm.set_value('tenure',r.agreement_tenure)
	})
},
property_address: function(frm){
	frm.set_value('property_address_detail', "");
	if (frm.doc.property_address!=undefined){
	frappe.call({
		method: "frappe.contacts.doctype.address.address.get_address_display",
		args: {"address_dict": frm.doc.property_address},
		callback: function(r) {
			if(r.message) {
				frm.set_value('property_address_detail', r.message);
			}
		}
	});
}
},
onload:function(frm){
	if(frm.doc.sales_order==undefined && frm.doc.project!=undefined && frm.doc.__islocal){
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.sales_order.get_rent_distribution_table",
			args: {
				docname: frm.doc.project,
				doctype:"Project"
				
			},
			callback: function (data) {
				if (Array.isArray(data.message)){
					$.each(data.message[0] || [], function (i, v) {
						var d = cur_frm.add_child("rent_distribution")
						d.from_month = v.from_month
						d.to_month = v.to_month
						d.rent = v.rent
					})
					cur_frm.refresh_field("rent_distribution")
				}
				else{
					frm.set_value('property_rent',data.message.rent)
				}
	
			}
		})
	}
}

})
