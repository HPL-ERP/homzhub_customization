from __future__ import unicode_literals
import frappe
from frappe.contacts.doctype.address.address import get_address_display

def validate(doc,method):
	if doc.get('__islocal') and doc.get('project'):
		project=frappe.get_doc('Project',doc.get('project'))
		doc.owner_name=project.owner_name
		doc.property_owner_=project.property_owner
		for d in project.tenant_list:
			doc.append("tenant_list",{'tenant':d.tenant,'tenant_name':d.tenant_name})
		doc.project_address=project.property_address
		doc.address_details=get_address_display({"address_dict": project.property_address})
		doc.agreement_start_=project.agreement_start_date
		doc.agreement_end=project.agreement_end_date

def after_insert(doc,method):
	from frappe.desk.form import assign_to
	if doc.get('project'):
		pro_doc=frappe.get_doc("Project",doc.get('project'))
		if pro_doc.get('project_template'):
			designation=[]
			pt_doc=frappe.get_doc('Project Template',pro_doc.project_template)
			if pro_doc.project_template:
				for d in pt_doc.tasks:
					if d.subject==doc.get('subject'):
						for p in pro_doc.participant_list:
							if p.designation == d.designation:
								assign_to.add({
									"assign_to": p.user,
									"doctype": "Task",
									"name":doc.get('name'),
									"description": doc.get('subject')
								})
