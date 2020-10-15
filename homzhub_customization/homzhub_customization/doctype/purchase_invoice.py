import frappe

def validate(doc,method):
	total=0
	for d in doc.get('taxes'):
		total+=round(d.tax_amount)
		d.tax_amount=round(d.tax_amount)

def on_create_gl_entry(doc,method):
	if doc.get('voucher_type')=="Purchase Invoice" :
		si=frappe.get_doc('Purchase Invoice',doc.get('voucher_no'))
		for d in si.get('taxes'):
			if d.account_head==doc.account:
				frappe.db.set_value(doc.doctype,doc.name,'credit',d.tax_amount)
				frappe.db.set_value(doc.doctype,doc.name,'credit_in_account_currency',d.tax_amount)