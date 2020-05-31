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
		cur_frm.doc.items.forEach(function(itm){
		itm.rate=(parseInt(itm.service_charges_in_per)/100*parseInt(frm.doc.property_rent))
	})
}
})
