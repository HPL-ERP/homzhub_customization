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
	if (frm.doc.is_selling_property_==1){
		cur_frm.doc.items.forEach(function(itm){
		itm.rate=(parseInt(itm.service_charges_in_per)/100*parseInt(frm.doc.property_rate))
	})
	}
},
is_selling_property_:function(frm){
	// console.log('*********',frm.doc.is_selling_property_)
		if (frm.doc.is_selling_property_==1){
			console.log('*********',frm.doc.project)
			 frappe.db.get_value("Project", {"name":frm.doc.project},"property_rate", function(r){
	      	 frm.set_value('property_rate',r.property_rate)
			})
		}
	else{
			frm.set_value('property_rate','')
		}

},
project:function(frm){
	frappe.db.get_value("Project", {"name":frm.doc.project},["property_address","address_detail"], function(r){
	      	 frm.set_value('property_address',r.property_address)
	      	 frm.set_value('property_address_detail',r.address_detail)
	})
}

})
