import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_field = {
		"Customer": [
			{
				"fieldname": "credit_limits_ct",
				"label": "Grace Limit",
				"fieldtype": "Table",
				"insert_after": "credit_limits",
				"options":"Customer Grace Limit CT",
				"is_custom_field":1,
				"is_system_generated":0				
			}
		]
	}
	create_custom_fields(custom_field, update=1)