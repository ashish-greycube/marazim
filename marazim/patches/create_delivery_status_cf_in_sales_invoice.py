import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_field = {
		"Sales Invoice": [
			{
				"fieldname": "delivery_status_cf",
				"label": "Delivery Status",
				"fieldtype": "Select",
				"insert_after": "update_billed_amount_in_sales_order",
				"options": "\nCreated\nDelivered\nPartial Delivered\nCancelled\nReceived",
				"read_only":1,
				"is_custom_field":1,
				"is_system_generated":0,
				"allow_on_submit":1,
				"translatable":0,
				"no_copy":1
			},			
		]
	}
	create_custom_fields(custom_field, update=1)