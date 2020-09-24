from __future__ import unicode_literals
from frappe.utils.data import nowdate, getdate
from frappe.utils import date_diff, add_months, today,add_days
import frappe,json

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
def fetch_participant_table(designation,table):
    users=[]
    duplicate=[]
    for d in json.loads(table):
        duplicate.append(d.get('user'))
        users.append({'user_id':d.get('user'),'name':d.get('employee'),'employee_name':d.get('employee_name'),'designation':d.get('designation')})
    for d in frappe.get_all('Employee',filters={'designation':designation},fields=['name','employee_name','user_id','designation']):
        if frappe.db.exists('User',d.user_id) and d.user_id not in duplicate:
            users.append(d)
    return users

@frappe.whitelist()
def fetch_department_participant_table(department,table):
    users=[]
    duplicate=[]
    for d in json.loads(table):
        duplicate.append(d.get('user'))
        users.append({'user_id':d.get('user'),'name':d.get('employee'),'employee_name':d.get('employee_name'),'designation':d.get('designation')})
    for d in frappe.get_all('Employee',filters={'department':department},fields=['name','employee_name','user_id','designation']):
        if frappe.db.exists('User',d.user_id) and d.user_id not in duplicate:
            users.append(d)
    return users
    

@frappe.whitelist()
def set_inventory_details(inventory_details,address):
    add_doc=frappe.get_doc('Address',address)
    table=[]
    if add_doc:
        add_doc.inventory_details=[]
        for d in json.loads(inventory_details):
            add_doc.append('inventory_details', {
                'asset': d.get('asset'),
                'quantity': d.get('quantity'),
                'description': d.get('description')
            })
            
        add_doc.save()  

@frappe.whitelist()
def get_contact_list(tenant):
    contact_list=[]
    for d in frappe.get_all('Dynamic Link',filters={'link_name':tenant,'parenttype':'Contact'},fields=['parent']):
        doc=frappe.get_doc('Contact',d.parent)
        contact_list.append({
            'contact':doc.name,
            'first_name':doc.first_name,
            'middle_name':doc.middle_name,
            'last_name':doc.last_name
        })
    return contact_list
