# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "homzhub_customization"
app_title = "homzhub_customization"
app_publisher = "Homzhub"
app_description = "homzhub_customization"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "varade.suraj787@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

scheduler_events = {
    "cron": {
        "* * * * *": [
            "frappe.email.queue.flush"
        ]
    }
}
# include js, css files in header of desk.html
# app_include_css = "/assets/homzhub_customization/css/homzhub_customization.css"
# app_include_js = "/assets/homzhub_customization/js/homzhub_customization.js"

# include js, css files in header of web template
# web_include_css = "/assets/homzhub_customization/css/homzhub_customization.css"
# web_include_js = "/assets/homzhub_customization/js/homzhub_customization.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
				"Project":"public/js/project.js",
				"Sales Order":"public/js/sales_order.js",
				"Sales Invoice":"public/js/sales_invoice.js",
				"Subscription":"public/js/subscription.js",
				"Journal Entry":"public/js/journal_entry.js",
				"Quotation":"public/js/quotation.js",
				"Expense Claim":"public/js/expense_claim.js",
				"Task":"public/js/task.js",
}	
doctype_list_js = {
	"Quotation":"public/js/quotation_list.js",
	"Sales Order":"public/js/sales_order_list.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "homzhub_customization.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "homzhub_customization.install.before_install"
# after_install = "homzhub_customization.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "homzhub_customization.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
	"Project": {
		"validate":"homzhub_customization.homzhub_customization.doctype.project.validate",
		"on_trash":"homzhub_customization.homzhub_customization.doctype.project.on_delete_project",
		"after_insert":"homzhub_customization.homzhub_customization.doctype.project.after_insert",

	},
	"Employee": {
		"validate":"homzhub_customization.homzhub_customization.doctype.employee.validate_employee"
	},
	"Subscription": {
		"validate":["homzhub_customization.homzhub_customization.doctype.sales_invoice.update_status",
		"homzhub_customization.homzhub_customization.doctype.subscription.validate"]
	},
	"Task": {
		"after_insert":["homzhub_customization.homzhub_customization.doctype.task.after_insert"],
		"validate":"homzhub_customization.homzhub_customization.doctype.task.validate"
	},
	"Issue": {
		"after_insert":"homzhub_customization.homzhub_customization.doctype.auto_share.on_save"
	},
	"Attendance Request": {
		"validate":"homzhub_customization.homzhub_customization.doctype.employee.validate_attendance_request"
	},
	"Sales Invoice":{
		"validate":["homzhub_customization.homzhub_customization.doctype.sales_invoice.validate"],
		"on_submit":"homzhub_customization.homzhub_customization.doctype.sales_invoice.on_submit",
		"on_trash":"homzhub_customization.homzhub_customization.doctype.sales_invoice.remove_from_project"
	},
	"Journal Entry":{
		"validate":["homzhub_customization.homzhub_customization.doctype.quotation.validate"],
		"on_submit":"homzhub_customization.homzhub_customization.doctype.quotation.update_amount_for_status"
	},
	"Employee Onboarding":{
		"on_change":"homzhub_customization.homzhub_customization.doctype.project.delete_project_made_from_emp_onboarding"
	},
	"ToDo":{
		"validate":"homzhub_customization.homzhub_customization.doctype.todo.validate",
		"on_change":"homzhub_customization.homzhub_customization.doctype.todo.on_delete"
	},
	"GL Entry":{
		"on_change":["homzhub_customization.homzhub_customization.doctype.sales_invoice.on_create_gl_entry",
					"homzhub_customization.homzhub_customization.doctype.gl_entry.after_insert",
					"homzhub_customization.homzhub_customization.doctype.purchase_invoice.on_create_gl_entry"]
	},
	"Sales Order":{
		"validate":"homzhub_customization.homzhub_customization.doctype.sales_order.validate"
	},
	"Purchase Order":{
		"validate":"homzhub_customization.homzhub_customization.doctype.purchase_order.validate"
	},
	"Purchase Invoice":{
		"validate":"homzhub_customization.homzhub_customization.doctype.sales_order.validate"
	},
	"Comment":{
		"validate":"homzhub_customization.homzhub_customization.doctype.comment.comment"
	},


}

scheduler_events = {
	"daily": [
		"homzhub_customization.homzhub_customization.doctype.custom_notification.weekly_auto_email",
		"homzhub_customization.homzhub_customization.doctype.custom_notification.execute",
		"homzhub_customization.homzhub_customization.doctype.rent_transaction.rent_transaction.create_document",
		"homzhub_customization.homzhub_customization.doctype.sales_invoice.delete_zero_amount_invoice"
	]
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# # 	"all": [
# # 		"homzhub_customization.tasks.all"
# # 	],
#  	# "daily": [
#  	# 	"homzhub_customization.homzhub_customization.doctype.custom_notification.weekly_auto_email",
# 	# 	"homzhub_customization.homzhub_customization.doctype.custom_notification.execute"
#  	# ]
# # 	"hourly": [
# # 		"homzhub_customization.tasks.hourly"
# # 	],
# # 	"weekly": [
# # 		"homzhub_customization.tasks.weekly"
# # 	]
# # 	"monthly": [
# # 		"homzhub_customization.tasks.monthly"
# # 	]
#  }

# Testing
# -------

# before_tests = "homzhub_customization.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "homzhub_customization.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "homzhub_customization.task.get_dashboard_data"
# }

