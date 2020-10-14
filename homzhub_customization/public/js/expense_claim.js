frappe.ui.form.on('Expense Claim', {
	claim_type: function(frm) {
        if (frm.doc.claim_type=="Client Expense"){
            frm.set_df_property('customer', 'reqd', 1);
        }

	},
})