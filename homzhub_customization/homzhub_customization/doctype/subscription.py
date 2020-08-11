from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions

from frappe.utils.data import nowdate, getdate, cint, add_days, date_diff, get_last_day, add_to_date, flt
	

def process(doc):
	"""
	To be called by task periodically. It checks the subscription and takes appropriate action
	as need be. It calls either of these methods depending the `Subscription` status:
	1. `process_for_active`
	2. `process_for_past_due`
	"""
	if doc.status == 'Active':
		process_for_active(doc)
	# elif doc.status in ['Past Due Date', 'Unpaid']:
	#     process_for_past_due_date(doc)

	doc.save()

def process_for_active(doc):
	"""
	Called by `process` if the status of the `Subscription` is 'Active'.

	The possible outcomes of this method are:
	1. Generate a new invoice
	2. Change the `Subscription` status to 'Past Due Date'
	3. Change the `Subscription` status to 'Cancelled'
	"""
	if not is_current_invoice_paid(doc) and (is_postpaid_to_invoice(doc) or is_prepaid_to_invoice(doc)):
		generate_invoice(doc)
		if current_invoice_is_past_due(doc):
			doc.status = 'Past Due Date'

	if current_invoice_is_past_due(doc) and getdate(nowdate()) > getdate(doc.current_invoice_end):
		doc.status = 'Past Due Date'

	if doc.cancel_at_period_end and getdate(nowdate()) > getdate(doc.current_invoice_end):
		cancel_subscription_at_period_end(doc)

def is_current_invoice_paid(doc):
	if is_new_subscription(doc):
		return False

	last_invoice = frappe.get_doc('Sales Invoice', doc.invoices[-1].invoice)
	if getdate(last_invoice.posting_date) == getdate(doc.current_invoice_start) and last_invoice.status == 'Paid':
		return True
	
	return False

def is_postpaid_to_invoice(doc):
	return getdate(nowdate()) > getdate(doc.current_invoice_end) or \
		(getdate(nowdate()) >= getdate(doc.current_invoice_end) and getdate(doc.current_invoice_end) == getdate(doc.current_invoice_start)) and \
		not has_outstanding_invoice(doc)

def is_prepaid_to_invoice(doc):
	if not doc.create_inv:
		return False

	if is_new_subscription(doc):
		return True

	# Check invoice dates and make sure it doesn't have outstanding invoices
	return getdate(nowdate()) >= getdate(doc.current_invoice_start) and not has_outstanding_invoice(doc)

def generate_invoice(doc, prorate=0):
	"""
	Creates a `Sales Invoice` for the `Subscription`, updates `doc.invoices` and
	saves the `Subscription`.
	"""
	invoice = create_invoice(doc,prorate)
	doc.append('invoices', {'invoice': invoice.name})
	doc.save()

	return invoice

def current_invoice_is_past_due(doc, current_invoice=None):
	"""
	Returns `True` if the current generated invoice is overdue
	"""
	if not current_invoice:
		current_invoice = get_current_invoice(doc)

	if not current_invoice:
		return False
	else:
		return getdate(nowdate()) > getdate(current_invoice.due_date)

def cancel_subscription_at_period_end(doc):
	"""
	Called when `Subscription.cancel_at_period_end` is truthy
	"""
	doc.status = 'Cancelled'
	if not doc.cancelation_date:
		doc.cancelation_date = nowdate()

def is_new_subscription(doc):
	"""
	Returns `True` if `Subscription` has never generated an invoice
	"""
	return len(doc.invoices) == 0

def has_outstanding_invoice(doc):
	"""
	Returns `True` if the most recent invoice for the `Subscription` is not paid
	"""
	current_invoice = get_current_invoice(doc)
	if not current_invoice:
		return False
	else:
		return not is_not_outstanding(current_invoice)

def create_invoice(doc, prorate):
	"""
	Creates a `Sales Invoice`, submits it and returns it
	"""
	invoice = frappe.new_doc('Sales Invoice')
	invoice.set_posting_time = 1
	# invoice.posting_date = doc.current_invoice_start
	invoice.customer = doc.customer
	invoice.subscription=doc.name
	invoice.project=doc.project
	# if doc.invoice_date and invoice.posting_date!=doc.invoice_date:
	invoice.posting_date=doc.invoice_date if doc.invoice_date else doc.current_invoice_start
	if doc.invoice_due_days:
		invoice.due_date=add_days(invoice.posting_date,doc.invoice_due_days)
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
			'due_date': invoice.due_date,
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

def get_current_invoice(doc):
	"""
	Returns the most recent generated invoice.
	"""
	if len(doc.invoices):
		current = doc.invoices[-1]
		if frappe.db.exists('Sales Invoice', current.invoice):
			doc = frappe.get_doc('Sales Invoice', current.invoice)
			return doc
		else:
			frappe.throw(_('Invoice {0} no longer exists'.format(current.invoice)))

# @staticmethod
def is_not_outstanding(invoice):
	"""
	Return `True` if the given invoice is paid
	"""
	return invoice.status == 'Paid'

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
		if len(plans)<2 and doc.custom_rate>0:
			if not prorate:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': doc.custom_rate})
			else:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': (doc.custom_rate * prorate_factor)})
		elif frappe.db.get_value('Subscription Plan',plan.plan,'price_determination')=='Percentage of Rent':
			from homzhub_customization.homzhub_customization.doctype.sales_invoice import get_plan_rate
			rate,srv_chg=get_plan_rate(doc,plan.plan, plan.qty, customer)
			if not prorate:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': rate,'service_charges_in_per':srv_chg})
			else:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': (rate * prorate_factor)})
		else:
			from erpnext.accounts.doctype.subscription_plan.subscription_plan import get_plan_rate
			if not prorate:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': get_plan_rate(plan.plan, plan.qty, customer)})
			else:
				items.append({'item_code': item_code, 'qty': plan.qty, 'rate': (get_plan_rate(plan.plan, plan.qty, customer) * prorate_factor)})
		

	return items

def get_prorata_factor(period_end, period_start):
	diff = flt(date_diff(nowdate(), period_start) + 1)
	plan_days = flt(date_diff(period_end, period_start) + 1)
	prorate_factor = diff / plan_days

	return prorate_factor

def validate(doc,method):
	if doc.get('project') and doc.get('invoice_date'):
		expected_date=frappe.db.get_value('Project',doc.get('project'),'expected_start_date')
		if  getdate(expected_date) > getdate(doc.get('invoice_date')):
			frappe.throw("<b>Invoice Date</b> must be equal or greater than project's <b>Expected Start Date</b>")
	if doc.get('customer') and doc.get('project'):
		if doc.get('customer') !=frappe.db.get_value('Project',doc.get('project'),'customer'):
			frappe.throw("<b>Project's customer</b> and <b>Subscription customer</b> must be equal")