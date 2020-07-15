from __future__ import unicode_literals
from frappe.utils.data import nowdate, getdate
import frappe
from frappe.utils import date_diff, add_months, today

def validate_employee(doc,method):
    for emp in frappe.get_all('Employee',fields=['name','first_name','middle_name','last_name','gender','date_of_birth','date_of_joining']):
        if doc.get("__islocal") and doc.get('first_name') == emp.get('first_name') and doc.get('middle_name') == emp.get('middle_name') and doc.get('last_name') == emp.get('last_name') and \
            doc.get('gender') == emp.get('gender') and getdate(doc.get('date_of_birth')) == getdate(emp.get('date_of_birth')) and getdate(doc.get('date_of_joining')) == getdate(emp.get('date_of_joining')):
            frappe.throw("Employee <b> <a href='#Form/Employee/{0}'>{0}</a></b> Already Exist".format(emp.name))
    
    import datetime
    d1 = datetime.datetime.strptime(doc.date_of_birth, '%Y-%m-%d')
    d2 = datetime.datetime.strptime(today(), '%Y-%m-%d')
    diff = (d2 - d1).total_seconds() / 60 / 60 /24 / 365.25
    if diff <= 10:
        frappe.throw("<b>Date Of Birth</b> can't be within last 10 years")
            