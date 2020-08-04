# from __future__ import unicode_literals
# import frappe

# def set_date(doc,method):
#     for d in doc.invoices:
#         invoice_doc=frappe.get_doc('Sales Invoice',d.invoice)
#         if doc.invoice_date and invoice_doc.posting_date!=doc.invoice_date:
#             frappe.db.set_value('Sales Invoice',d.invoice,'posting_date',doc.invoice_date)