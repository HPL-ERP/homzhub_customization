cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Subscription'
		],
		'label': 'Others'
	},
]);

frappe.ui.form.on('Sales Order Item', {
    item_code:function(frm,cdt, cdn){
        var row = locals[cdt][cdn]
        frappe.db.get_value("Item", {"name":row.item_code},"service_charges_in_per", function(r){
        row.service_charges_in_per=r.service_charges_in_per
		})
    },
})

frappe.ui.form.on('Sales Order', {
validate:function(frm){
	if(frm.doc.based_on_rent==1){
		frappe.call({
			method:
			"homzhub_customization.homzhub_customization.doctype.sales_order.item_table_calculation",
			args: {
				doc:cur_frm.doc	
			},
			callback: function (data) {
				$.each(data.message[0] || [], function (i, v) {
					cur_frm.doc.items.forEach(function(itm){
				  if(itm.item_code==i){
					 itm.rate=v
					 }
				 })
			 })
	
			}
		})
	}
},
onload:function(frm){
	if(frm.doc.project!=undefined && frm.doc.__islocal){
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
}
})

	