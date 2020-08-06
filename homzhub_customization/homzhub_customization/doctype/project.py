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
