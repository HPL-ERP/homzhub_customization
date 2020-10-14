from __future__ import unicode_literals
import frappe

def execute():
	expense_claim()
	project_subscription_plan()

def expense_claim():
	print('********************Expense Claim*********************')
	for d in frappe.get_all('Expense Claim'):
		print(d.name)
		frappe.db.set_value('Expense Claim',d.name,'payable_account','Creditors - HAPL')

def project_subscription_plan():
	print('*************Project Subscription********************')
	for d in frappe.get_all('Project'):
		print(d.name)
		doc=frappe.get_doc('Project',d.name)
		doc.set('subscription_plans',[])
		for sub in frappe.get_all('Subscription',filters={'project':d.name}):
			sub_doc=frappe.get_doc('Subscription',sub.name)
			for pl in sub_doc.plans:
				doc.append("subscription_plans", {
				"subscription" : sub.name,
				"subscription_plan" :  pl.plan
				})
		doc.save()   

def set_participant_table_default_values():
	# bench execute homzhub_customization.homzhub_customization.doctype.patches.set_participant_table_default_values
	
	for p in frappe.get_all('Project'):
		doc=frappe.get_doc('Project',p.name)
		user=[]
		for d in doc.get('participant_list'):
			user.append(d.get('user'))
		for name in ['karan.nashine@homzhub.com','awantika.raut@homzhub.com']:
			if name not in user:
				doc.append("participant_list", {
					"user" : name,
					"employee" :frappe.db.get_value('Employee', {'user_id': name}, 'name'),
					"employee_name":frappe.db.get_value('Employee', {'user_id': name}, 'employee_name','designation'),
					"designation":frappe.db.get_value('Employee', {'user_id': name}, 'designation')
					})
		doc.save()