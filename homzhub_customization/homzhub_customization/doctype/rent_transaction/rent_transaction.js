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
	},
	rent_recieved(frm){
		if(!frm.doc.receive_date && frm.doc.rent_recieved==1){
			frm.set_value('rent_recieved',0)
			frappe.throw(__("Please Enter Receive Date") )
		}
	},
	rent_transffered(frm){
		if(!frm.doc.transfer_date && frm.doc.rent_transffered==1){
			frm.set_value('rent_transffered',0)
			frappe.throw(__("Please Enter Transfer Date") )
		}
	},
	include_in_bulk_transaction(frm){
		if(frm.doc.include_in_bulk_transaction==1){
			// frm.remove_custom_button("Receive Rent")
			frm.set_df_property("receive_rent","hidden",1)
			if(frm.doc.__islocal) {
				frappe.throw(__("Please Save Document first") )
			}
		var dialog = new frappe.ui.Dialog({
			'fields': [
				{fieldname: 'journal_entry',label:'Journal Entry', fieldtype: 'Link', options:'Journal Entry',
					change: function () {
						frappe.db.get_value("Journal Entry", {"name":dialog.get_value('journal_entry')},["cheque_date","total_credit","cheque_no"], function(r){
							dialog.set_value('total_credit',r.total_credit)
							dialog.set_value('reference_date',r.cheque_date)
							frm.set_value('receive_date',r.cheque_date)
							frm.set_value('received_reference_no',r.cheque_no)
							frm.set_value('rent_recieved',1)
							})
					}
				},
				{fieldname: 'total_credit',label:'Total Credit', fieldtype: 'Data',read_only:1},
				{fieldname: 'reference_date',label:'Reference Date', fieldtype: 'Data',read_only:1}
			],
			primary_action: function(){
				dialog.hide();
				frm.set_value("payment_entries",[])
				var d = cur_frm.add_child("payment_entries")
				d.account_entries=dialog.get_value('journal_entry')
				cur_frm.refresh_field("payment_entries")
				show_alert({
					message: __('Successfully Done'),
					indicator: 'green'
				});
			},
			primary_action_label: __('Insert')
		})
		dialog.show();
	}
}
	})