# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def validate(doc,method):
	if doc.reference_type in ['Task','Issue'] and len(frappe.get_all('User Permission',filters={'allow':doc.reference_type,'for_value':doc.reference_name,'user':doc.owner}))==0:
		permission=frappe.new_doc('User Permission')
		permission.user=doc.owner
		permission.allow=doc.reference_type
		permission.for_value=doc.reference_name
		permission.apply_to_all_doctypes=1
		permission.save()

def on_delete(doc,method):
	if doc.status=="Cancelled":
		permissionList=frappe.get_all('User Permission',filters={'allow':doc.reference_type,'for_value':doc.reference_name,'user':doc.owner})
		if doc.reference_type in ['Task','Issue'] and len(permissionList)!=0:
			for d in permissionList:
				frappe.delete_doc('User Permission',d.name)
