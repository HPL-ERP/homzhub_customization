# Copyright (c) 2013, suraj varade and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute():
	# bench execute homzhub_customization.homzhub_customization.patches.set_value_from_project_to_task.execute
	for p in frappe.get_all('Project',):
		pro=frappe.get_doc('Project',p.name)
		for d in frappe.get_all('Task',{'project':p.name}):
			doc=frappe.get_doc('Task',d.name)
			doc.property_owner_=pro.property_owner
			doc.owner_list=[]
			for own in pro.get('owner_list'):
				doc.append('owner_list', {
					'prop_owner':own.get('prop_owner'),
					'owner_name':own.get('owner_name')
				})
			doc.owner_name=pro.owner_name
			doc.project_address=pro.property_address
			doc.address_details=pro.address_detail
			doc.save()
			