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
	// 	cur_frm.doc.items.forEach(function(itm){
	// 	itm.rate=(parseInt(itm.service_charges_in_per)/100*parseInt(frm.doc.property_rent))
	// })
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
