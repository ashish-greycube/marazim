# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters : filters = {}

    columns, customer_data = [], []
    columns = get_columns()
    customer_data = get_data(filters)

    if not customer_data:
        frappe.throw("No data found")
        return columns, customer_data
    
    return columns, customer_data

def get_columns():
    return[
        {
            "fieldname" : "date",
            "fieldtype" : "Date",
            "label" : "Date",
            "width" : 130
        },
        {
            "fieldname" : "day",
            "fieldtype" : "Data",
            "label" : "Day",
            "width" : 130
        },
        {
            "fieldname" : "name",
            "fieldtype" : "Link",
            "options" : "Customer Visit",
            "label" : "Visit No",
            "width" : 150
        },
        {
            "fieldname" : "customer",
            "fieldtype" : "Link",
            "label" : "Customer",
            "options" : "Customer",
            "width" : 250
        },
        {
            "fieldname" : "territory",
            "fieldtype" : "Link",
            "label" : "Territory",
            "options" : "Territory",
            "width" : 150
        },
        {
            "fieldname" : "customer_group",
            "fieldtype" : "Link",
            "label" : "Customer Group",
            "options": "Customer Group",
            "width" : 200
        },
        {
            "fieldname" : "purpose_of_visit",
            "fieldtype" : "Select",
            "label" : "Purpose",
            "width" : 170
        },
        {
            "fieldname" : "docstatus",
            "fieldtype" : "Data",
            "label" : "Status",
            "width" : 100
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)

    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    data = frappe.db.sql("""select
					date,
					day,
					name,
					customer,
					territory,
					customer_group,
					docstatus,
					purpose_of_visit
				from
					`tabCustomer Visit`
				where
					date between '{0}' and '{1}' {2}
            """.format(from_date, to_date,conditions),as_dict=True,debug=1)

    if len(data) >0:
        for row in data:
            if row.docstatus == 0:
                print("draft")
                row.docstatus = "Draft"
            if row.docstatus == 1:
                row.docstatus = "Submitted"
            if row.docstatus == 2:
                row.docstatus = "Cancelled"
    return data

def get_conditions(filters):
    conditions = ""

    if filters.get("customer"):
        conditions += " and customer = '{0}'".format(filters.get("customer"))
    if filters.get('sales_partner'):
        conditions += "and sales_partner='{0}'".format(filters.get('sales_partner'))
    if filters.get('territory'):
        conditions += "and territory='{0}'".format(filters.get('territory'))
    if filters.get('customer_group'):
        conditions += "and customer_group='{0}'".format(filters.get('customer_group'))
    if filters.get('status'):
        doc_status = None
        if filters.get('status') == "Draft":
            doc_status=0
        elif filters.get('status') == "Submitted":
            doc_status=1
        elif filters.get('status') == "Cancelled":
            doc_status=2
        conditions += "and docstatus='{0}'".format(doc_status)

    return conditions