import frappe

def validate(doc,method):
	total=0
	for d in doc.get('taxes'):
		total+=round(d.tax_amount)
		d.tax_amount=round(d.tax_amount)