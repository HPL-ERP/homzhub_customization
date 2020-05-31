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
onload:function(frm){
	if(frm.doc.project!=undefined){
	frappe.db.get_value("Project", {"name":frm.doc.project},['property_rent','tenure'], function(r){
		frm.set_value('property_rent',r.property_rent)
		frm.set_value('tenure',r.tenure)
		})
	}
},
validate:function(frm){
		cur_frm.doc.items.forEach(function(itm){
		itm.rate=((parseInt(frm.doc.tenure)*parseInt(frm.doc.property_rent))*(parseInt(itm.service_charges_in_per)/100))
	})
}
})