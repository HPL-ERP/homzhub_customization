frappe.ui.form.on('Quotation', {
	refresh: function(frm) {
		frm.add_custom_button('Journal Entry', () => {

		frappe.model.open_mapped_doc({
			method: "homzhub_customization.homzhub_customization.doctype.quotation.make_journal_entry",
			frm: me.frm
		})

		},
		__('Create')
		)	

	}
})