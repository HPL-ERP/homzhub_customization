from __future__ import unicode_literals
from frappe.utils.data import nowdate, getdate
from frappe.utils import date_diff, add_months, today,add_days
import frappe

def validate_dates(doc,method):
    if doc.expected_start_date and  doc.expected_end_date:
        if doc.expected_start_date >= doc.expected_end_date:
                frappe.throw('Expected End Date Must Be Greater Than Start Date')

    if doc.agreement_start_date and  doc.agreement_end_date:
        if doc.agreement_start_date >= doc.agreement_end_date:
            frappe.throw('Agreement End Date Must Be Greater Than Start Date')

    if doc.get('lock_in_period_start'):
    	doc.lock_in_period_end=add_months(doc.get('lock_in_period_start'),doc.get('lock_in_period'))

@frappe.whitelist()
def fetch_inventory_table(address):
    doc=frappe.get_doc('Address',address)
    items=[]
    for d in doc.inventory_details:
        items.append({'asset':d.asset,'quantity':d.quantity,'description':d.description})
    return items

@frappe.whitelist()
def fetch_participant_table(designation):
    users=[]
    for d in frappe.get_all('Employee',filters={'designation':designation},fields=['name','employee_name','user_id','designation']):
        if frappe.db.exists('User',d.user_id):
            users.append(d)
    return users