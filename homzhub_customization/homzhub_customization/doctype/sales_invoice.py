from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.subscription_plan.subscription_plan import get_plan_rate
from frappe.utils.data import nowdate, getdate, cint, add_days, date_diff, get_last_day, add_to_date, flt
from erpnext.accounts.doctype.subscription.subscription import process
	
def get_plan_rate(doc,plan, quantity=1, customer=None):
	rate=0
	plan = frappe.get_doc("Subscription Plan", plan)
	if doc.property_rent:
		rate=int(doc.property_rent)*int(doc.agreement_tenure)	
	if doc.rent_distribution:
		for table in doc.rent_distribution:
			rate+=(int(table.to_month)-int(table.from_month)+1)*int(table.rent)
	return rate*(int(plan.rate)/100),plan.rate

def execute(doc,method):
	set_project_and_subscription_to_invoice(doc,method)

def set_project_and_subscription_to_invoice(doc,method):
	for d in doc.invoices:
		frappe.db.set_value('Sales Invoice',d.invoice,'project',doc.project)
		frappe.db.set_value('Sales Invoice',d.invoice,'subscription',doc.name)

def get_items_from_plans(doc, plans, prorate=0):
	"""
	Returns the `Item`s linked to `Subscription Plan`
	"""
	if prorate:
		prorate_factor = get_prorata_factor(doc.current_invoice_end, doc.current_invoice_start)

	items = []
	customer = doc.customer
	for plan in plans:
		item_code = frappe.db.get_value("Subscription Plan", plan.plan, "item")
		rate,srv_chg=get_plan_rate(doc,plan.plan, plan.qty, customer)
		if doc.custom_rate>0:
			if not prorate:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': doc.custom_rate})
			else:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': (doc.custom_rate * prorate_factor)})
		else:
			if not prorate:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': rate,'service_charges_in_per':srv_chg})
			else:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': (rate * prorate_factor)})

	return items

def get_prorata_factor(period_end, period_start):
	diff = flt(date_diff(nowdate(), period_start) + 1)
	plan_days = flt(date_diff(period_end, period_start) + 1)
	prorate_factor = diff / plan_days

	return prorate_factor

def create_invoice(doc, prorate):
	"""
	Creates a `Sales Invoice`, submits it and returns it
	"""
	invoice = frappe.new_doc('Sales Invoice')
	invoice.set_posting_time = 1
	invoice.posting_date = doc.current_invoice_start
	invoice.customer = doc.customer

	## Add dimesnions in invoice for subscription:
	accounting_dimensions = get_accounting_dimensions()

	for dimension in accounting_dimensions:
		if doc.get(dimension):
			invoice.update({
				dimension: doc.get(dimension)
			})

	# Subscription is better suited for service items. I won't update `update_stock`
	# for that reason
	items_list = get_items_from_plans(doc,doc.plans, prorate)
	for item in items_list:
		invoice.append('items',	item)

	# Taxes
	if doc.tax_template:
		invoice.taxes_and_charges = doc.tax_template
		invoice.set_taxes()

	# Due date
	invoice.append(
		'payment_schedule',
		{
			'due_date': add_days(doc.current_invoice_end, cint(doc.days_until_due)),
			'invoice_portion': 100
		}
	)

	# Discounts
	if doc.additional_discount_percentage:
		invoice.additional_discount_percentage = doc.additional_discount_percentage

	if doc.additional_discount_amount:
		invoice.discount_amount = doc.additional_discount_amount

	if doc.additional_discount_percentage or doc.additional_discount_amount:
		discount_on = doc.apply_additional_discount
		invoice.apply_discount_on = discount_on if discount_on else 'Grand Total'

	# Subscription period
	invoice.from_date = doc.current_invoice_start
	invoice.to_date = doc.current_invoice_end

	invoice.flags.ignore_mandatory = True
	invoice.save()
	invoice.submit()

	return invoice

def generate_sales_invoice(doc, prorate=0):
	"""
	Creates a `Sales Invoice` for the `Subscription`, updates `self.invoices` and
	saves the `Subscription`.
	"""
	invoice = create_invoice(doc,prorate)
	doc.append('invoices', {'invoice': invoice.name})
	doc.save()

	return invoice

@frappe.whitelist()
def get_subscription_updates(name):
	"""
	Use this to get the latest state of the given `Subscription`
	"""
	subscription = frappe.get_doc('Subscription', name)
	if frappe.db.get_value('Subscription Plan',subscription.plans[0].plan,'price_determination')=='Percentage of Rent':
		generate_sales_invoice(subscription)
	elif subscription.custom_rate>0:
		generate_sales_invoice(subscription)
	else:
		subscription.process()




		