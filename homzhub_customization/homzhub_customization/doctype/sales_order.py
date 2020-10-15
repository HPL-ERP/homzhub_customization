from __future__ import unicode_literals
import frappe
import json
from frappe.utils.data import flt

def validate(doc,method):
	total=0
	for d in doc.get('taxes'):
		total+=round(d.tax_amount)
		d.tax_amount=round(d.tax_amount)

@frappe.whitelist()
def get_rent_distribution_table(docname,doctype):
	if doctype=="Project":
		if frappe.db.get_value('{0}'.format(doctype),docname,'varying_rent')==1:
			return get_table(docname,doctype)
		else:
			return get_rent(docname,doctype)

	else:
		if frappe.db.get_value('{0}'.format(doctype),docname,'property_rent'):
			return get_rent(docname,doctype)
		else:
			return get_table(docname,doctype)

def get_table(docname,doctype):
	table=frappe.db.sql("""
		select * from `tabVarying Rent` 
		where parent='{0}' and 
		parenttype='{1}' 
		order by idx""".format(docname,doctype), as_dict=1)
	return table,frappe.db.get_value('{0}'.format(doctype),docname,'agreement_tenure')

def get_rent(docname,doctype):
	property_rent,tenure=frappe.db.get_value('{0}'.format(doctype),docname,['property_rent','agreement_tenure'])
	return {'rent':property_rent,'tenure':tenure}

@frappe.whitelist()
def item_table_calculation(doc):
	doc=json.loads(doc)
	rate=0
	if doc.get('property_rent'):
		rate=int(doc.get('property_rent'))*int(11)	
	if doc.get('rent_distribution'):
		for table in doc.get('rent_distribution'):
			rate+=(int(table.get('to_month'))-int(table.get('from_month'))+1)*flt(table.get('rent'))
	item_list=[]
	for d in doc.get('items'):
		if d.get('service_charges_in_per'):
			item_list.append({d.get('item_code'):d.get('qty')*rate*(int(d.get('service_charges_in_per'))/100)})
		else:
			frappe.throw("Please add <b>Service Charges In Per</b> for item <b>'{0}'</b>".format(d.get('item_code')))
	return item_list
