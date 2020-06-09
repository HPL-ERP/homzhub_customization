from __future__ import unicode_literals
import frappe

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

