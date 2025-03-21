from . import __version__ as app_version

app_name = "marazim"
app_title = "Marazim"
app_publisher = "GreyCube Technologies"
app_description = "Customization for Marazim"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/marazim/css/marazim.css"
# app_include_js = "/assets/marazim/js/marazim.js"

# include js, css files in header of web template
# web_include_css = "/assets/marazim/css/marazim.css"
# web_include_js = "/assets/marazim/js/marazim.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "marazim/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Payment Entry" : "public/js/payment_entry.js",
              "Sales Invoice" : "public/js/sales_invoice.js",
              "Customer":"public/js/customer.js"}
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

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "marazim.install.before_install"
after_install = "marazim.api.after_install_run_patches"

# Uninstallation
# ------------

# before_uninstall = "marazim.uninstall.before_uninstall"
# after_uninstall = "marazim.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "marazim.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Stock Entry": {
        "on_submit":  "marazim.api.end_transit_in_stock_entry",
    },
	"Sales Invoice": {
        "validate":"marazim.api.check_qty_against_warehouse",
		"on_submit": [
            "marazim.api.check_grace_days_and_amount_for_si",
            "marazim.api.auto_create_dn_from_si",
            ]
	},
	"Delivery Note": {
		"on_submit": ["marazim.api.update_delivery_status_cf_of_sales_invoice_from_dn"],
        "on_cancel": ["marazim.api.update_delivery_status_cf_of_sales_invoice_from_dn"]
	}    
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
        "0 1 * * *": [
            "marazim.api.create_daily_customer_visit",
        ]
    },
}

# Testing
# -------

# before_tests = "marazim.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "marazim.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "marazim.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Request Events
# ----------------
# before_request = ["marazim.utils.before_request"]
# after_request = ["marazim.utils.after_request"]

# Job Events
# ----------
# before_job = ["marazim.utils.before_job"]
# after_job = ["marazim.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"marazim.auth.validate"
# ]

