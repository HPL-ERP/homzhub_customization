# -*- coding: utf-8 -*-
# Copyright (c) 2020, Homzhub and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt,today

class RentTransaction(Document):
	def make_journal_entry_from_receive_rent(self):	
		doc=frappe.new_doc('Journal Entry')
		doc.voucher_type="Bank Entry"
		doc.append("accounts", {
			"account": "NACH - HAPL",
			"credit_in_account_currency": flt(self.rent_amount)
		})
		doc.append("accounts", {
			"account": "HDFC - HAPL",
			"debit_in_account_currency": flt(self.rent_amount)
		
		})
		doc.cheque_no=self.received_reference_no
		doc.cheque_date=self.receive_date
		doc.user_remark="Rent Received from "+self.tenant_name
		doc.posting_date=self.receive_date
		doc.insert()
		doc.submit()
		self.rent_recieved=1
		self.status="Rent Received"
	def make_journal_entry_from_transfer_rent(self):
		doc=frappe.new_doc('Journal Entry')
		doc.voucher_type="Bank Entry"
		doc.append("accounts", {
			"account": "NACH - HAPL",
			"credit_in_account_currency": flt(self.rent_amount)
		})
		doc.append("accounts", {
			"account": "HDFC - HAPL",
			"debit_in_account_currency": flt(self.rent_amount)
		
		})
		doc.cheque_no=self.transfer_reference_no
		doc.cheque_date=self.transfer_date
		doc.user_remark="Rent Transfer To "+self.owner_name
		doc.posting_date=self.transfer_date
		doc.insert()
		doc.submit()
		self.rent_transffered=1
		self.status="Rent Transffered"

def create_document():
	from datetime import date
	today = date.today()
	if today==today.replace(day=1):
		for project in frappe.get_all('Project'):
			pro=frappe.get_doc('Project',project.name)
			for sub in frappe.get_all('Subscription',filters={'project':project.name},fields=['name','current_invoice_start','current_invoice_end','rent_auto_deduct']):
				plan=frappe.db.get_value('Subscription Plan Detail',{'parent':sub.name},'plan')
				if plan and plan == 'Homzhub Comfort':
					doc=frappe.new_doc('Rent Transaction')
					doc.project=pro.name
					doc.subscription=sub.name
					doc.owner=pro.property_owner
					doc.posting_date=today
					doc.owner_name=pro.owner_name
					doc.subscription_plan=plan
					doc.subscription_start_date=sub.current_invoice_start
					doc.subscription_end_date=sub.current_invoice_end
					doc.tenant=pro.property_tenant
					doc.tenant_name=pro.tenant_name
					doc.agreement_start=pro.agreement_start_date
					doc.agreement_end=pro.agreement_end_date
					doc.agreement_tenure=pro.agreement_tenure
					doc.rent_amount= pro.property_rent if pro.fixed_rent==1 else ''
					doc.rent_auto_deduct=sub.rent_auto_deduct
					doc.save()

@frappe.whitelist()
def get_fields(project):
	from frappe.utils import today
	fields={
			'subscription':'','owner':'','owner_name':'','posting_date':today(),'subscription_plan':'','subscription_start_date':'',
			'subscription_end_date':'','tenant':'','tenant_name':'','agreement_start':'','agreement_end':'',
			'agreement_tenure':'','rent_amount':'' ,'rent_auto_deduct':''
			}
	pro=frappe.get_doc('Project',project)
	for sub in frappe.get_all('Subscription',filters={'project':project},fields=['name','current_invoice_start','current_invoice_end','rent_auto_deduct']):
		plan=frappe.db.get_value('Subscription Plan Detail',{'parent':sub.name},'plan')
		if plan and plan == 'Homzhub Comfort':
			fields={
			'subscription':sub.name,
			'owner':pro.property_owner,
			'posting_date':today(),
			'owner_name':pro.owner_name,
			'subscription_plan':plan,
			'subscription_start_date':sub.current_invoice_start,
			'subscription_end_date':sub.current_invoice_end,
			'tenant':pro.property_tenant,
			'tenant_name':pro.tenant_name,
			'agreement_start':pro.agreement_start_date,
			'agreement_end':pro.agreement_end_date,
			'agreement_tenure':pro.agreement_tenure,
			'rent_amount':pro.property_rent if pro.fixed_rent==1 else '' ,
			'rent_auto_deduct':sub.rent_auto_deduct
			}
	return fields
			