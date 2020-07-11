// Copyright (c) 2020, Homzhub and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rent Transaction', {
	project(frm){
		frappe.call({
			method: "homzhub_customization.homzhub_customization.doctype.rent_transaction.rent_transaction.get_fields",
			args: {
				'project':frm.doc.project
			},
			callback: function(r) {
			Object.keys(r.message).forEach(i=>{
				frm.set_value(i,r.message[i])
				
				})
			}
		});
	
	},
	receive_rent(frm){
		if(!frm.doc.__islocal) {
		if(!frm.doc.received_reference_no){
			frappe.throw(__("Please Fill Field <b>Received Reference No</b>") )
		}
		else if(!frm.doc.receive_date){
			frappe.throw(__("Please Fill Field <b>Receive Date</b>") )
		}
		else{
			frappe.confirm(
			__('you want to create account entry for Recieve Rent?'),
				function() {
						frappe.call({
							doc: frm.doc,
							method: 'make_journal_entry_from_receive_rent',
							callback: function() {
								frm.refresh();
							}
						});
				}
			);
		}
		}
		else{
			frappe.throw(__("Please Save Document first") )
		}
	},
	transfer_rent(frm){
		if(!frm.doc.__islocal) {
		if(!frm.doc.transfer_reference_no){
			frappe.throw(__("Please Fill Field <b>Transfer Reference No</b>") )
		}
		else if(!frm.doc.transfer_date){
			frappe.throw(__("Please Fill Field <b>Transfer Date</b>") )
		}
		else{
		 frappe.confirm(
			__('you want to create account entry for Transfer Rent?'),
				function() {
						frappe.call({
							doc: frm.doc,
							method: 'make_journal_entry_from_transfer_rent',
							callback: function() {
								frm.refresh();
							}
						});
				}
			);
		}
		}
		 else{
			frappe.throw(__("Please Save Document first") )
		}
	}
	})