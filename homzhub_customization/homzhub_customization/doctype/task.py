from __future__ import unicode_literals
import frappe

def validate(doc,method):
	if doc.get('__islocal') and doc.get('project'):
		project=frappe.get_doc('Project',doc.get('project'))
		doc.owner_name=project.owner_name
		doc.property_owner_=project.property_owner
		for d in project.tenant_list:
			doc.append("tenant_list",{'tenant':d.tenant,'tenant_name':d.tenant_name})
		doc.project_address=project.property_address
		doc.address_details=project.address_detail
		doc.agreement_start_=project.agreement_start_date
		doc.agreement_end=project.agreement_end_date