from __future__ import unicode_literals
from frappe.utils.data import nowdate, getdate
import frappe

def validate_employee(doc,method):
    for emp in frappe.get_all('Employee',fields=['name','first_name','middle_name','last_name','gender','date_of_birth','date_of_joining']):
        if doc.get('first_name') == emp.get('first_name') and doc.get('middle_name') == emp.get('middle_name') and doc.get('last_name') == emp.get('last_name') and \
            doc.get('gender') == emp.get('gender') and getdate(doc.get('date_of_birth')) == getdate(emp.get('date_of_birth')) and getdate(doc.get('date_of_joining')) == getdate(emp.get('date_of_joining')):
            frappe.throw("Employee <b> <a href='#Form/Employee/{0}'>{0}</a></b> Already Exist".format(emp.name))
            