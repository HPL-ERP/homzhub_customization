# Copyright (c) 2013, suraj varade and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.utils import get_url_to_form
from frappe.utils import date_diff, add_months, today, getdate, add_days, flt, get_last_day

def execute():
    for us in frappe.get_all('User',fields=['name','email','full_name']):
        data1=[]
        data2=[]
        data3=[]
        for ds in frappe.get_all('DocShare',filters={'user':us.name,'share_doctype':'Task'}):
            doc=frappe.get_doc('DocShare',ds.name)
            task,project,status,subject,time,start_date,end_date=frappe.db.get_value('Task',{'name':doc.share_name},['name','project','status','subject','expected_time','exp_start_date','exp_end_date'])
            if start_date and end_date:
                start_date=start_date.strftime("%d-%m-%Y")
                end_date=end_date.strftime("%d-%m-%Y")
            else:
                start_date='-'
                end_date='-'
            if not project:
                project='-'
            if task and status=='Open':
                data1.append({'project':project,'task_id':task,'task_name':subject,'start_date':start_date,'end_date':end_date,'status':status,'time':time})
            if task and status=='Overdue':
                data2.append({'project':project,'task_id':task,'task_name':subject,'start_date':start_date,'end_date':end_date,'status':status})
        open_task_send_msg(data1,us)
        overdue_task_send_msg(data2,us)

        for ds in frappe.get_all('DocShare',filters={'user':us.name,'share_doctype':'Issue'}):
            doc=frappe.get_doc('DocShare',ds.name)
            issue,customer,status,subject,date=frappe.db.get_value('Issue',{'name':doc.share_name},['name','customer','status','subject','opening_date'])
            if date:
                date=date.strftime("%d-%m-%Y")
            else:
                date='-'
            if not customer:
                customer='-'
            if issue and status=='Open':
                data3.append({'customer':customer,'issue_id':issue,'issue_name':subject,'status':status,'date':date})
        open_issue_send_msg(data3,us)

def open_task_send_msg(data,us):
    msg=''
    if len(data)>0:
        msg="""<p>Hi {0}</p><br>""".format(us.get('full_name'))
        msg+="""<b>{0} Task</b><br>""".format(data[0].get('status'))
        msg += """</u></b></p><table class='table table-bordered'><tr>
            <th>Task ID</th><th>Subject</th><th>Estimated Hrs</th><th>Expected Start Date</th><th>Expected End Date</th><th>Project</th><th>User Name</th>"""
        for d in data:
            msg += "<tr><td>" + """<a href="{0}">{1}</a>""".format(get_url_to_form('Task',d.get('task_id') ), str(d.get('task_id'))) + "</td><td>" + str(d.get('task_name')) + "</td><td>" + str(d.get('time')) + "</td><td>" + str(d.get('start_date'))  + "</td><td>" + str(d.get('end_date'))  + "</td><td>"  + """<a href="{0}">{1}</a>""".format(get_url_to_form('Project',d.get('project') ), str(d.get('project'))) + "</td><td>" + str(us.get('full_name')) + "</td></tr>"
        msg += "</table>"
        frappe.sendmail(recipients=us.email,subject='Task Notification',message = msg)


def overdue_task_send_msg(data,us):
    msg=''
    if len(data)>0:
        msg="""<p>Hi {0}</p><br>""".format(us.get('full_name'))
        msg+="""<b>{0} Task</b><br>""".format(data[0].get('status'))
        msg += """</u></b></p><table class='table table-bordered'><tr>
             <th>Task ID</th><th>Subject</th><th>Expected Start Date</th><th>Expected End Date</th><th>Project</th><th>User Name</th>"""
        for d in data:
            msg += "<tr><td>" + """<a href="{0}">{1}</a>""".format(get_url_to_form('Task',d.get('task_id') ), str(d.get('task_id'))) + "</td><td>" + str(d.get('task_name')) + "</td><td>" + str(d.get('start_date'))  + "</td><td>" + str(d.get('end_date'))  + "</td><td>"  + """<a href="{0}">{1}</a>""".format(get_url_to_form('Project',d.get('project') ), str(d.get('project'))) + "</td><td>" + str(us.get('full_name')) + "</td></tr>"
        msg += "</table>"
        frappe.sendmail(recipients=us.email,subject='Task Notification',message = msg)

def open_issue_send_msg(data,us):
    msg=''
    if len(data)>0:
        msg="""<p>Hi {0}</p><br>""".format(us.get('full_name'))
        msg+="""<b>{0} Issue</b><br>""".format(data[0].get('status'))
        msg += """</u></b></p><table class='table table-bordered'><tr>
            <th>Issue ID</th><th>Subject</th><th>Date</th><th>Customer</th><th>Project</th>"""
        for d in data:
            project=frappe.db.get_value('Issue',d.get('issue_id'),'project')
            if not project:
                project='-'
            msg += "<tr><td>" + """<a href="{0}">{1}</a>""".format(get_url_to_form('Issue',d.get('issue_id') ), str(d.get('issue_id'))) + "</td><td>" + str(d.get('issue_name')) + "</td><td>" + str(d.get('date'))  + "</td><td>"  + """<a href="{0}">{1}</a>""".format(get_url_to_form('Customer',d.get('customer') ), str(d.get('customer'))) + "</td><td>"  + """<a href="{0}">{1}</a>""".format(get_url_to_form('Project',project ), str(project)) + "</td></tr>"
        msg += "</table>"
        frappe.sendmail(recipients=us.email,subject='Issue Notification',message = msg)

def weekly_auto_email():
    from datetime import date
    import calendar
    current_date = date.today()
    if calendar.day_name[current_date.weekday()] == 'Sunday':
        start_date=add_days(today(), -7)
        end_date = today()
        next_date=start_date
        date_list=[]
        while end_date!=next_date:
            date_list.append(next_date)
            next_date=add_days(next_date, 1)
        import datetime
        for emp in frappe.get_all('Employee',filters={'status':'Active'}):
            timesheet_date=[]
            remaining_hr=[]
            for t in frappe.get_all('Timesheet',filters={'employee':emp.name,'start_date': ['between', [start_date, end_date]]},fields=['name','start_date','total_hours']):
                if t.get('start_date') and t.get('total_hours')>=8:
                    timesheet_date.append(t.get('start_date').strftime('%Y-%m-%d'))
                else:
                    remaining_hr.append({t.get('start_date').strftime('%Y-%m-%d'):t.get('total_hours')})
            email_dates=date_list
            if timesheet_date:
                diff=list(set(date_list) - set(timesheet_date))
                email_dates=sorted(diff, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
            timesheet_auto_email(emp.name,email_dates,remaining_hr)

def timesheet_auto_email(employee,dates,wk_hr):
    msg=''
    if len(dates)>0:
        from datetime import date 
        email,name,holiday_list=frappe.db.get_value('Employee',employee,['prefered_email','employee_name','holiday_list'])
        leave_dates=[]
        for d in frappe.get_all('Leave Application',filters={'employee':employee,'status':'Approved','docstatus':1},fields=['from_date','to_date']):
            next_date=getdate(d.get('from_date'))
            leave_dates.append(next_date.isoformat())
            while getdate(d.get('to_date'))!= next_date:
                next_date=add_days(next_date, 1)
                leave_dates.append(next_date.isoformat())
        msg="""<p>Hi {0}</p><br>""".format(name)
        msg+="""<b>Timesheet Records</b><br>"""
        msg += """</u></b></p><table class='table table-bordered'><tr>
            <th>Date</th><th>Timesheet</th><th>Actual Hours</th>"""
        holidays=[]
        from datetime import datetime
        for hl in frappe.get_all('Holiday',filters={'parent':holiday_list},fields=['holiday_date']):
            holidays.append(hl.get('holiday_date').strftime("%Y-%m-%d"))
        for d in dates:
            if d not in holidays and d not in leave_dates:
                hr=0
                timesheet=''
                for h in wk_hr:
                    if h.get(d):
                        timesheet=frappe.db.get_value('Timesheet',{'employee':employee,'start_date':d},'name')
                        hr=h.get(d)
                msg += "<tr><td>" + str(d) + "</td><td>" + """<a href="{0}">{1}</a>""".format(get_url_to_form('Timesheet',str(timesheet) ), str(timesheet)) + "</td><td>" + str(hr)  + "</td></tr>"
        msg += "</table>"
        frappe.sendmail(recipients=email,subject='Timesheet Notification',message = msg)
