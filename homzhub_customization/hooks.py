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
		"validate":"homzhub_customization.homzhub_customization.doctype.project.validate_dates"
	},
	"Employee": {
		"validate":"homzhub_customization.homzhub_customization.doctype.employee.validate_employee"
	}
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"homzhub_customization.tasks.all"
# 	],
# 	"daily": [
# 		"homzhub_customization.tasks.daily"
# 	],
# 	"hourly": [
# 		"homzhub_customization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"homzhub_customization.tasks.weekly"
# 	]
# 	"monthly": [
# 		"homzhub_customization.tasks.monthly"
# 	]
# }

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

