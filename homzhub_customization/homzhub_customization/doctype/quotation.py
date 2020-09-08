from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_journal_entry(source_name, target_doc=None, skip_item_mapping=False):
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		if source.project:
			target.update({'project': source.project})

	mapper = {
		"Quotation": {
			"doctype": "Journal Entry",
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}

	target_doc = get_mapped_doc("Quotation", source_name, mapper, target_doc, set_missing_values)

	return target_doc

def validate(doc,method):
	if doc.project:
		for item in doc.accounts:
			item.project=doc.project

def update_amount_for_status(doc,method):
	if doc.quotation:
		quotation=frappe.get_doc('Quotation',doc.quotation)
		for d in doc.accounts:
			if d.party==quotation.get('party_name'):
				frappe.db.set_value('Quotation',quotation.name,'journal_entry',1)
		if quotation.amount>0:
			frappe.db.set_value('Quotation',quotation.name,'amount',quotation.amount-doc.total_debit)

				
			



