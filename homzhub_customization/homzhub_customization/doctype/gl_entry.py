import frappe

def after_insert(doc,method):
    if doc.docstatus==1 and doc.get('voucher_type')=='Expense Claim' and 'Creditors' not in doc.get('account'):
        exDoc=frappe.get_doc('Expense Claim',doc.get('voucher_no'))
        if exDoc.claim_type=='Client Expense':
            if 'Debtors' not in doc.get('account'):
                doc.cancel()
                new=frappe.new_doc('GL Entry')
                new.posting_date=doc.posting_date
                new.account="Debtors - HAPL"
                new.party_type="Customer"
                new.party=exDoc.customer
                new.debit= exDoc.grand_total
                new.cost_center=doc.cost_center
                new.account_currency=doc.account_currency
                new.debit_in_account_currency=doc.debit_in_account_currency
                new.against=doc.against
                new.voucher_no=doc.voucher_no
                new.voucher_type=doc.voucher_type
                new.save()
                new.submit()
                frappe.delete_doc('GL Entry',doc.name)