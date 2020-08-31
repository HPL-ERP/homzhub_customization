from __future__ import unicode_literals
from frappe.utils.data import nowdate, getdate
import frappe,json
from frappe.utils import date_diff, add_months, today,add_days,today

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

def validate_attendance_request(doc,method):
    if doc.get("__islocal"):
        # import datetime
        # now = datetime.datetime.now()
        # today8am = now.replace(hour=8, minute=45, second=0, microsecond=0)
        # today3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)
        # roles = frappe.get_roles(frappe.session.user)
        
        # if not (today8am < now  and  now < today3pm) and  "HR Manager" not in roles: 
        #     frappe.throw("Please raise your attendace request between 8:45 AM to 3 PM")
        user = frappe.session.user
        if getdate(today())!=getdate(doc.get('from_date')) and getdate(today())!=getdate(doc.get('to_date')) and ("HR Manager" not in frappe.get_roles(user)):
            frappe.throw("You can not record back dated attendance request")  
        date_list1=[]
        next_date1=getdate(doc.get('from_date'))
        date_list1.append(next_date1)
        while getdate(doc.get('to_date'))!= next_date1:
            next_date1=add_days(next_date1, 1)
            date_list1.append(getdate(next_date1))

        date_list2=[]
        for cust in frappe.get_all('Attendance Request',filters={'employee':doc.employee},fields=['name','from_date','to_date','employee']):
            next_date2=getdate(cust.get('from_date'))
            date_list2.append(next_date2)
            while getdate(cust.get('to_date'))!= next_date2:
                next_date2=add_days(next_date2, 1)
                date_list2.append(getdate(next_date2))

            for d in date_list1:
                if d in date_list2:
                    frappe.throw("Attendance Request <b><a href='#Form/Attendance Request/{0}'>{0}</a></b> Already exist ".format(cust.name))

# def validate_attendance_time(doc,method):
#     if doc.get("__islocal"):
#         import datetime
#         now = datetime.datetime.now()
#         today8am = now.replace(hour=8, minute=45, second=0, microsecond=0)
#         today3pm = now.replace(hour=19, minute=0, second=0, microsecond=0)
#         roles = frappe.get_roles(frappe.session.user)
        
#         if not (today8am < now  and  now < today3pm) and  "HR Manager" not in roles: 
#             frappe.throw("Please raise your attendace request between 8:45 AM to 7 PM")
@frappe.whitelist()
def execute(emp,from_date,to_date):
    data=[]
    for d in frappe.get_all('Expense Claim',filters={'employee':emp,'posting_date':['between',(from_date,to_date)]},fields=['name','posting_date','employee_name','total_claimed_amount']):
        data.append(d)
    print(data)
    return data   
            