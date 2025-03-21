// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Visits Report"] = {
	"filters": [
        {
            "fieldname": "sales_partner",
            "label" : __("Sales Partner"),
            "fieldtype" : "Link",
            "options": "Sales Partner"
        },
        {
            "fieldname": "customer",
            "label" : __("Customer"),
            "fieldtype" : "Link",
            "options": "Customer"
        },
        {
            "fieldname": "territory",
            "label" : __("Territory"),
            "fieldtype" : "Link",
            "options": "Territory"
        },
        {
            "fieldname": "customer_group",
            "label" : __("Customer Group"),
            "fieldtype" : "Link",
            "options": "Customer Group"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options" : "\nDraft\nSubmitted\nCancelled",
        }
    ]
};
