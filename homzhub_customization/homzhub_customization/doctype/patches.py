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