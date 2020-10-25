# Copyright (c) 2013, suraj varade and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute():
	# bench execute homzhub_customization.homzhub_customization.patches.set_round_off_in_sales_invoice.execute
	for si in frappe.get_all('Sales Invoice',{'docstatus':1}):
		doc=frappe.get_doc('Sales Invoice',si.name)
		frappe.db.set_value('Sales Invoice',doc.name,'net_total',myround(doc.net_total))
		tax_total=0
		rtotal=0
		grand_total=0
		for d in doc.get('taxes'):
			rtotal+=d.tax_amount
			tax_total+=myround(d.tax_amount)
			frappe.db.set_value(d.doctype,d.name,'tax_amount',myround(d.tax_amount))
			frappe.db.set_value(d.doctype,d.name,'total',myround(d.total))
			frappe.db.set_value(d.doctype,d.name,'base_total',myround(d.base_total))
			frappe.db.set_value(d.doctype,d.name,'base_tax_amount',myround(d.base_tax_amount))
		frappe.db.set_value('Sales Invoice',doc.name,'rounding_adjustment',tax_total-rtotal)
		frappe.db.set_value('Sales Invoice',doc.name,'total_taxes_and_charges',tax_total)
		if doc.apply_discount_on=='Net Total':
			frappe.db.set_value('Sales Invoice',doc.name,'grand_total',(myround(doc.net_total)+tax_total))
		if doc.apply_discount_on=='Grand Total':
			frappe.db.set_value('Sales Invoice',doc.name,'grand_total',doc.rounded_total)
		for gl in frappe.get_all('GL Entry',{'voucher_type':'Sales Invoice','voucher_no':si.name},['name','account']):
			if gl.account=='Round Off - HAPL':
				if (tax_total-rtotal)>=0:
					frappe.db.set_value('GL Entry',gl.name,'credit',tax_total-rtotal)
					frappe.db.set_value('GL Entry',gl.name,'credit_in_account_currency',tax_total-rtotal)
				else:
					frappe.db.set_value('GL Entry',gl.name,'debit',tax_total-rtotal)
					frappe.db.set_value('GL Entry',gl.name,'debit_in_account_currency',tax_total-rtotal)
			for t in doc.get('taxes'):
				if t.account_head==gl.account:
					frappe.db.set_value('GL Entry',gl.name,'credit',myround(t.tax_amount))
					frappe.db.set_value('GL Entry',gl.name,'credit_in_account_currency',myround(t.tax_amount))
			
			if gl.account=='Debtors - HAPL':
				frappe.db.set_value('GL Entry',gl.name,'debit',doc.rounded_total)
				frappe.db.set_value('GL Entry',gl.name,'debit_in_account_currency',doc.rounded_total)


def myround(n):
	if round(n + 1) - round(n) == 1:
		return float(round(n))
	return n + abs(n) / n * 0.5