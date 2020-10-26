from __future__ import unicode_literals
from frappe.utils.data import nowdate, getdate
from frappe.utils import date_diff, add_months, today,add_days
import frappe,json
from frappe.share import add
from six import iteritems


def validate(doc,method):
	if doc.expected_start_date and  doc.expected_end_date:
		if doc.expected_start_date >= doc.expected_end_date:
				frappe.throw('Expected End Date Must Be Greater Than Start Date')

	if doc.agreement_start_date and  doc.agreement_end_date:
		if doc.agreement_start_date >= doc.agreement_end_date:
			frappe.throw('Agreement End Date Must Be Greater Than Start Date')

	if doc.get('lock_in_period_start'):
		if not doc.get('lock_in_period') and doc.get('lock_in_period') !=0:
			frappe.throw('Please fill <b>Lock In Period</b> field')
		doc.lock_in_period_end=add_months(doc.get('lock_in_period_start'),doc.get('lock_in_period'))

	for d in doc.get('participant_list'):
		if not doc.get('__islocal') and len(frappe.get_all('ToDo',filters={'owner':d.get('user'),'reference_type':doc.doctype,'reference_name':doc.name}))==0:
			todo=frappe.new_doc('ToDo')
			todo.reference_type=doc.doctype
			todo.reference_name=doc.name
			todo.owner=d.get('user')
			todo.description="Assignment for Project "+doc.name
			todo.save()
	
def after_insert(doc,method):
    for d in doc.get('participant_list'):
        if len(frappe.get_all('ToDo',filters={'owner':d.get('user'),'reference_type':doc.doctype,'reference_name':doc.name}))==0:
            todo=frappe.new_doc('ToDo')
            todo.reference_type=doc.doctype
            todo.reference_name=doc.name
            todo.owner=d.get('user')
            todo.description="Assignment for Project "+doc.name
            todo.save()
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
	for d in frappe.get_all('Employee',filters={'designation':designation,'status':'Active'},fields=['name','employee_name','user_id','designation']):
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
	for d in frappe.get_all('Employee',filters={'department':department,'status':'Active'},fields=['name','employee_name','user_id','designation']):
		if frappe.db.exists('User',d.user_id) and d.user_id not in duplicate:
			users.append(d)
	return users
	

@frappe.whitelist()
def set_inventory_details(doc):
	doc=json.loads(doc)
	add_doc=frappe.get_doc('Address',doc.get('property_address'))
	if add_doc:
		add_doc.inventory_details=[]
		for d in doc.get('inventory_list'):
			add_doc.append('inventory_details', {
				'asset': d.get('asset'),
				'quantity': d.get('quantity'),
				'description': d.get('description')
			})
		add_doc.electricity_status=[]
		for d in doc.get('electricity_billing'):
			add_doc.append('electricity_status', {
				'consumer_no': d.get('consumer_no'),
				'date': d.get('date'),
				'month': d.get('month'),
				'amount': d.get('amount'),
				'reading': d.get('reading'),
				'status': d.get('status')
			})

		add_doc.electricity_status=[]
		for d in doc.get('water_meter_billing'):
			add_doc.append('water_meter_bill', {
				'consumer_no': d.get('consumer_no'),
				'date': d.get('date'),
				'month': d.get('month'),
				'amount': d.get('amount'),
				'reading': d.get('reading'),
				'status': d.get('status')
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

def delete_project_made_from_emp_onboarding(doc,method):
	if doc.get('project') and frappe.db.exists('Project',doc.get('project')):
		frappe.db.set_value("Employee Onboarding",doc.name,'project','')
		frappe.delete_doc('Project',doc.get('project'))

def on_delete_project(doc,method):
	# removed project link from Task
	for t in frappe.get_all('Task',filters={'project':doc.name}):
		frappe.db.set_value('Task',t.name,'project','')

	# removed project link from Employee Onboarding
	for e in frappe.get_all('Employee Onboarding',filters={'project':doc.name}):
		frappe.db.set_value('Employee Onboarding',t.name,'project','')

@frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
def address_query(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import get_match_cond

	link_doctype = filters.pop('link_doctype')
	link_name_filter = filters.pop('link_name')
	link_name_filter=str(link_name_filter).replace('[','')
	link_name=str(link_name_filter).replace(']','')

	if not link_name:
		link_name='()'

	condition = ""
	meta = frappe.get_meta("Address")
	for fieldname, value in iteritems(filters):

		if meta.get_field(fieldname) or fieldname in frappe.db.DEFAULT_COLUMNS:
			condition += " and {field}={value}".format(
				field=fieldname,
				value=frappe.db.escape(value))

	searchfields = meta.get_search_fields()

	if searchfield and (meta.get_field(searchfield)\
				or searchfield in frappe.db.DEFAULT_COLUMNS):
		searchfields.append(searchfield)

	search_condition = ''
	for field in searchfields:
		if search_condition == '':
			search_condition += '`tabAddress`.`{field}` like %(txt)s'.format(field=field)
		else:
			search_condition += ' or `tabAddress`.`{field}` like %(txt)s'.format(field=field)

	return frappe.db.sql("""select
			`tabAddress`.name, `tabAddress`.city, `tabAddress`.country
		from
			`tabAddress`, `tabDynamic Link`
		where
			`tabDynamic Link`.parent = `tabAddress`.name and
			`tabDynamic Link`.parenttype = 'Address' and
			`tabDynamic Link`.link_doctype = %(link_doctype)s and
			`tabDynamic Link`.link_name IN ({link_name}) and
			ifnull(`tabAddress`.disabled, 0) = 0 and
			({search_condition})
			{mcond} {condition}
		order by
			if(locate(%(_txt)s, `tabAddress`.name), locate(%(_txt)s, `tabAddress`.name), 99999),
			`tabAddress`.idx desc, `tabAddress`.name
		limit %(start)s, %(page_len)s """.format(
			mcond=get_match_cond(doctype),
			key=searchfield,
			link_name=link_name,
			search_condition = search_condition,
			condition=condition or ""), {
			'txt': '%' + txt + '%',
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len,
			'link_doctype': link_doctype
		})

	   
