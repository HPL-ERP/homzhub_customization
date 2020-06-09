from __future__ import unicode_literals
import frappe
import json

@frappe.whitelist()
def get_rent_distribution_table(docname,doctype):
	if doctype=="Project":
		if frappe.db.get_value('{0}'.format(doctype),docname,'varying_rent')==1:
			return get_table(docname,doctype)
		else:
			return get_rent(docname,doctype)

	else:
		if frappe.db.get_value('{0}'.format(doctype),docname,'property_rent')==1:
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

def validate(doc,method):
	rate_calculation(doc)

def rate_calculation(doc):
	if doc.property_rent:
		rate=int(doc.property_rent)*int(doc.agreement_tenure)	
	if doc.rent_distribution:
		for table in doc.rent_distribution:
			rate+=(int(table.to_month)-int(table.from_month)+1)*int(table.rent)
	return rate*(int()/100),plan.rate

@frappe.whitelist()
def item_table_calculation(doc):
	doc=json.loads(doc)
	rate=0
	if doc.get('property_rent'):
		rate=int(doc.get('property_rent'))*int(doc.get('agreement_tenure'))	
	if doc.get('rent_distribution'):
		for table in doc.get('rent_distribution'):
			rate+=(int(table.get('to_month'))-int(table.get('from_month'))+1)*int(table.get('rent'))
	item_list=[]
	for d in doc.get('items'):
		if d.get('service_charges_in_per'):
			item_list.append({d.get('item_code'):d.get('qty')*rate*(int(d.get('service_charges_in_per'))/100)})
		else:
			frappe.throw("Please add <b>Service Charges In Per</b> for item <b>'{0}'</b>".format(d.get('item_code')))
	return item_list
