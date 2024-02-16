import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_field = {
		"Customer Credit Limit": [
			{
				"fieldname": "grace_days_cf",
				"label": "Grace Days",
				"fieldtype": "Int",
				"insert_after": "credit_limit",
				"description": "Days after which new sales invoice creation will stop if there are unpaid invoices.",
				"is_custom_field":1,
				"is_system_generated":0				
			},			
			{
				"fieldname": "grace_amount_cf",
				"label": "Grace Amount",
				"fieldtype": "Currency",
				"insert_after": "grace_days_cf",
				"description": "After grace days are over, the total amount of sales invoice for which creation shall be allowed.",
				"is_custom_field":1,
				"is_system_generated":0				
			}
		]
	}
	create_custom_fields(custom_field, update=1)