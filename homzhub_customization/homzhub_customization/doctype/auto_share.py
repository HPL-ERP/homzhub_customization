# Copyright (c) 2013, suraj varade and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.share import add

def on_save(doc,method):
	if doc.project:
		for ds in frappe.get_all('DocShare',filters={'share_doctype':'Project','share_name':doc.project}):
			ds_doc=frappe.get_doc('DocShare',ds.name)
			add(doc.doctype, doc.name, ds_doc.get("user"), read=ds_doc.read, write=ds_doc.write, share=ds_doc.share, everyone=ds_doc.everyone, flags={"ignore_share_permission":True}, notify=1)

	if not doc.project and doc.raised_by:
		customer=frappe.db.get_value('Customer',{'email_id':doc.raised_by})
		if customer:
			project=frappe.db.get_value('Project',{'customer':customer})
			if project:
				for ds in frappe.get_all('DocShare',filters={'share_doctype':'Project','share_name':project}):
					ds_doc=frappe.get_doc('DocShare',ds.name)
					add(doc.doctype, doc.name, ds_doc.get("user"), read=ds_doc.read, write=ds_doc.write, share=ds_doc.share, everyone=ds_doc.everyone, flags={"ignore_share_permission":True}, notify=1)
