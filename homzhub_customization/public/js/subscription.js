frappe.ui.form.on('Subscription', {
	onload:function(frm){
		if(frm.doc.sales_order!=undefined && frm.doc.project!=undefined && frm.doc.__islocal){
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.sales_order.get_rent_distribution_table",
			args: {
				docname: frm.doc.sales_order,
				doctype:"Sales Order"	
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
					frm.set_value('agreement_tenure',data.message[1])
				}
				else{
					frm.set_value('property_rent',data.message.rent)
					frm.set_value('agreement_tenure',data.message.tenure)
				}
	
			}
		})
	}
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
					frm.set_value('agreement_tenure',data.message[1])
				}
				else{
					frm.set_value('property_rent',data.message.rent)
					frm.set_value('agreement_tenure',data.message.tenure)
				}
	
			}
		})
	}
	frappe.db.get_value("Project", {"name":frm.doc.project},["agreement_start_date","agreement_end_date"], function(r){
		frm.set_value('agreement_start_date',r.agreement_start_date)
		frm.set_value('agreement_end_date',r.agreement_end_date)
		})
	},
	refresh: function(frm) {
		if(!frm.is_new()){
			if(frm.doc.status !== 'Cancelled'){
				frm.remove_custom_button('Fetch Subscription Updates')
				frm.add_custom_button(
					__('Fetch Subscription Updates'),
					() => frm.events.get_subscription_updates(frm)
				);
			}
		}
	},
	get_subscription_updates: function(frm) {
		const doc = frm.doc;
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.sales_invoice.get_subscription_updates",
			args: {name: doc.name},
			freeze: true,
			callback: function(data){
				if(!data.exc){
					frm.reload_doc();
				}
			}
		});
	},
	customer:function(frm){
		frappe.db.get_value("Customer", {"name":frm.doc.customer},"customer_name", function(r){
        	frm.set_value("customer_name",r.customer_name)
		})
	}

})
