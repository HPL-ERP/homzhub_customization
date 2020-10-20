from __future__ import unicode_literals
import frappe
from frappe.utils import get_url_to_form

def comment(doc,method):
    userList=[]
    for u in frappe.get_all('User'):
        userList.append(u.name)
    from bs4 import BeautifulSoup
    if doc.content:
        soup = BeautifulSoup(doc.content)
        if "data-id=" in doc.content:
            for d in doc.content.split("data-id="):
                if (d.split(' ')[0]).replace('"','') in userList:
                    user=(d.split(' ')[0]).replace('"','')
                    sub='You are mentioned by {0} in {1} document'.format(doc.comment_email,doc.reference_doctype)
                    msg="""<p>Hello {0},</p></br>""".format(frappe.db.get_value('User',user,'full_name'))
                    msg+="""<p>You're mentioned by {0} in Doctype <b>{1} {2}</b></p></br>""".format(doc.comment_email,doc.reference_doctype,doc.reference_name)
                    msg+='<p>"{0}"</p></br>'.format(soup.get_text())
                    msg+="""<p>Click here to check the document <a href="{0}">{1}</a></p>""".format(get_url_to_form(doc.reference_doctype,doc.reference_name), str(doc.reference_name))
                    frappe.sendmail(recipients=user,subject=sub,message =msg )