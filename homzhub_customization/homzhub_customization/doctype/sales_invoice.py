from __future__ import unicode_literals
import frappe,json
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions
from erpnext.accounts.doctype.subscription_plan.subscription_plan import get_plan_rate
from frappe.utils.data import nowdate, getdate, cint, add_days, date_diff, get_last_day, add_to_date, flt
from homzhub_customization.homzhub_customization.doctype.subscription import process

# from erpnext.accounts.doctype.subscription.subscription import process
	
def get_plan_rate(doc,plan, quantity=1, customer=None):
	rate=0
	plan = frappe.get_doc("Subscription Plan", plan)
	if doc.property_rent:
		rate=int(doc.property_rent)*int(plan.billing_interval_count)
	if doc.rent_distribution:
		for table in doc.rent_distribution:
			rate+=(int(table.to_month)-int(table.from_month)+1)*flt(table.rent)
	return rate*(int(plan.rate)/100),plan.rate

# def execute(doc,method):
# 	set_project_and_subscription_to_invoice(doc,method)

# def set_project_and_subscription_to_invoice(doc,method):
# 	for d in doc.invoices:
# 		frappe.db.set_value('Sales Invoice',d.invoice,'project',doc.project)
# 		frappe.db.set_value('Sales Invoice',d.invoice,'subscription',doc.name)

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
		if doc.custom_rate>0:
			if not prorate:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': doc.custom_rate})
			else:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': (doc.custom_rate * prorate_factor)})
		else:
			rate,srv_chg=get_plan_rate(doc,plan.plan, plan.qty, customer)
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
	# if frappe.db.get_value('Subscription Plan',subscription.plans[0].plan,'price_determination')=='Percentage of Rent':
	# 	generate_sales_invoice(subscription)
	# elif subscription.custom_rate>0 and len(subscription.plans)<2:
	# 	generate_sales_invoice(subscription)
	# else:
	if subscription.create_inv==1:
		process(subscription)

def update_status(doc,method):
	if doc.get('__islocal') and doc.invoice_date:
		doc.current_invoice_start=doc.invoice_date

	if len(doc.get('invoices'))<1 and doc.status in ['Past Due Date','Unpaid']:
		doc.status='Active'

def validate(doc,method):
	doc.net_total=myround(doc.net_total)
	tax_total=0
	rtotal=0
	grand_total=0
	for d in doc.get('taxes'):
		rtotal+=d.tax_amount
		tax_total+=myround(d.tax_amount)
		d.tax_amount=myround(d.tax_amount)
		d.total=myround(d.total)
		d.base_total=myround(d.base_total)
		d.base_tax_amount=myround(d.base_tax_amount)
	doc.rounding_adjustment=tax_total-rtotal
	doc.total_taxes_and_charges=tax_total
	if doc.apply_discount_on=='Net Total':
		doc.grand_total=(myround(doc.net_total)+tax_total)
	if doc.get('subscription'):
		subsc=frappe.get_doc('Subscription',doc.get('subscription'))
		sub_dates=[]
		next_date=getdate(subsc.current_invoice_start)
		sub_dates.append(next_date.isoformat())
		while getdate(subsc.current_invoice_end)!= next_date:
			next_date=add_days(next_date, 1)
			sub_dates.append(next_date.isoformat())
		for d in frappe.get_all("Sales Invoice",filters={'subscription':doc.get('subscription')},fields=['name','from_date','to_date']):
			next_date=getdate(d.get('from_date'))
			if next_date.isoformat() in sub_dates and doc.name!=d.name and doc.amended_from:
				frappe.throw("Invoice <b><a href='#Form/Sales Invoice/{0}'>{0}</a></b> Alredy Exist Between Dates".format(d.name))
			while getdate(d.get('to_date'))!= next_date:
				next_date=add_days(next_date, 1)
				if next_date.isoformat() in sub_dates and doc.name!=d.name:
					frappe.throw("Invoice <b><a href='#Form/Sales Invoice/{0}'>{0}</a></b> Alredy Exist Between Dates".format(d.name))
	if doc.due_days:
		doc.due_date=add_days(doc.posting_date,doc.due_days)
		frappe.db.set_value('Sales Invoice',doc.name,'due_date',add_days(doc.posting_date,doc.due_days))

def myround(n):
    if round(n + 1) - round(n) == 1:
        return float(round(n))
    return n + abs(n) / n * 0.5

def on_submit(doc,method):
	if doc.get('project') and not doc.get('subscription'):
		pro_doc=frappe.get_doc('Project',doc.get('project'))
		for d in doc.get('items'):
			pro_doc.append("invoiced_items", {
			"invoice" : doc.get('name'),
			"item" : d.get('item_code'),
			'qty':d.get('qty')
			})
		pro_doc.save()
	if doc.sales_order:
		frappe.db.set_value('Sales Order', doc.sales_order,'status','Invoiced')

def remove_from_project(doc,method):
	if doc.get('project') and not doc.get('subscription'):
		pro_doc=frappe.get_doc('Project',doc.get('project'))
		new_list=pro_doc.get('invoiced_items')
		pro_doc.set('invoiced_items',[])
		for d in new_list:
			if doc.get('name') !=d.get('invoice'):
				pro_doc.append("invoiced_items", {
				"invoice" : doc.get('name'),
				"item" : d.get('item_code'),
				'qty':d.get('qty')
				})
		pro_doc.save()

def on_create_gl_entry(doc,method):
	if doc.get('voucher_type')=="Sales Invoice" :
		si=frappe.get_doc('Sales Invoice',doc.get('voucher_no'))
		for d in si.get('taxes'):
			if d.account_head==doc.account:
				frappe.db.set_value(doc.doctype,doc.name,'credit',d.tax_amount)
				frappe.db.set_value(doc.doctype,doc.name,'credit_in_account_currency',d.tax_amount)

def delete_zero_amount_invoice():
	for i in frappe.get_all('Sales Invoice',{'total':0},['name','total']):
		for si in frappe.get_all('Subscription Invoice',{'invoice':i.name},['name','parent']):
			frappe.delete_doc('Subscription Invoice',si.name)
		doc=frappe.get_doc('Sales Invoice',i.name)
		doc.cancel()
		frappe.delete_doc('Sales Invoice',doc.name)

@frappe.whitelist()
def get_customer_list(customer):
	for pro in frappe.get_all('Project',{'status':('!=','Cancelled')}):
		doc=frappe.get_doc('Project',pro.name)
		if doc.get('customer')==customer:
			return pro.name
		customer_list=[]
		for own in doc.get('owner_list'):
			customer_list.append(own.prop_owner)
		if customer in customer_list:
			return pro.name

@frappe.whitelist()
def make_project(doc):
	doc=json.loads(doc)
	pro=frappe.new_doc('Project')
	pro.project_name=doc.get('project_name')
	pro.project_template=doc.get('project_template')
	pro.expected_start_date=doc.get('expected_start_date')
	pro.expected_end_date=doc.get('expected_end_date')
	pro.project_type=doc.get('project_type')
	pro.property_address=doc.get('property_address')
	for own in doc.get('owner_list'):
		pro.append("owner_list", {
			"prop_owner" : own.get('prop_owner'),
			"owner_name" : own.get('owner_name')
			})
	for ten in doc.get('tenant_list'):
		pro.append("tenant_list", {
			"tenant" : ten.get('tenant'),
			"tenant_name" : ten.get('tenant_name')
			})
	pro.save()
	return pro.name


