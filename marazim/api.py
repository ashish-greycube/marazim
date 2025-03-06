import frappe
from erpnext.selling.doctype.customer.customer import get_credit_limit, get_customer_outstanding
from frappe.utils import add_days,getdate,flt
from frappe import _, msgprint, throw
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from frappe.utils import get_link_to_form, today, nowdate, get_weekday
from erpnext.stock.doctype.stock_entry.stock_entry import make_stock_in_entry
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_return
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def get_grace_details(customer, company):
	grace_details = None

	if customer:
		grace_details = frappe.db.get_value(
			"Customer Grace Limit CT",
			{"parent": customer, "parenttype": "Customer", "company": company},
			["grace_days_cf","grace_amount_cf"], as_dict=1
		)

	return grace_details


def get_customer_outstanding_si(customer, company,grace_details):
	grace_date=add_days(getdate(),-(grace_details. grace_days_cf))
	print('grace_date',grace_date)
	outstanding_si_amount = frappe.db.sql(
		"""select
			sum(si.outstanding_amount) as total_outstanding_amount
		from `tabSales Invoice` si
		where
			si.customer=%s and si.company=%s
			and si.docstatus = 1 and si.posting_date <= %s
		group by si.customer
		""",
		(customer, company,grace_date),
		as_dict=True,debug=1
	)	
	if len(outstanding_si_amount)>0:
		return  outstanding_si_amount[0].total_outstanding_amount
	else:
		return 0

def check_grace_days_and_amount_for_si(self,method):
	company=self.company
	customer=self.customer
	grace_details = get_grace_details(customer, company)
	if not grace_details:
		return

	customer_outstanding = get_customer_outstanding_si(customer, company, grace_details)
	#  this means there is outstanding older than grace days
	if customer_outstanding > 0:
		if grace_details.grace_amount_cf >0:
			if flt(customer_outstanding) > grace_details.grace_amount_cf:
				message=(_("Grace limit has been crossed for customer {0}.<br> Total outstanding is {1} <br> Allowed grace days are {2} <br>Grace amount allowed after grace days is {3}")
			  .format(customer, customer_outstanding,grace_details.grace_days_cf ,grace_details.grace_amount_cf))
				frappe.throw(message)
		else:
			message=(_("Grace limit has been crossed for customer {0}.<br> Total outstanding is {1} <br> Allowed grace days are {2}")
			.format(customer, customer_outstanding,grace_details.grace_days_cf))
			frappe.throw(message)

def auto_create_dn_from_si(self,method):
	if self.is_return==0 and self.update_stock==0:
		dn_creted=make_delivery_note(self.name)
		if dn_creted:
			dn=dn_creted.save(ignore_permissions=True)
			frappe.db.set_value("Sales Invoice", self.name, 'delivery_status_cf', 'Created')
			msg_dn_st="Sales Invoice {0} delivery status is changed to {1}".format(self.name,'Created')
			frappe.msgprint(msg_dn_st,alert=1)
			dn_creted.add_comment('Comment', text=msg_dn_st)		
			
			msg="Delivery Note {0} is auto created<br> Please ensure DN is submitted before SI return is done".format(get_link_to_form("Delivery Note",dn.name))
			frappe.msgprint(msg)
			self.add_comment('Comment', text=msg)

	elif self.is_return==1 and self.update_stock==0:
		# find the DN created and submitted, and do a new return DN such that qty are as per SI return
		if self.return_against:
			connected_delivery_notes=find_connected_delivery_notes(self.return_against)
			if connected_delivery_notes and len(connected_delivery_notes)>0:
				for dn in connected_delivery_notes:
					create_returned_dn=make_sales_return(dn.name)
					to_remove = []
					for dn_return in create_returned_dn.items:
						found_si_item=False
						for si_return in self.items:
							if dn_return.item_code==si_return.item_code:
								found_si_item=True
								dn_return.qty=si_return.qty
								break
						if found_si_item==False:
							to_remove.append(dn_return)
					[create_returned_dn.items.remove(d) for d in to_remove]
					returned_dn=create_returned_dn.save(ignore_permissions=True)
					# when return SI is created, SI_return.dn_status='Created'
					frappe.db.set_value("Sales Invoice", self.name, 'delivery_status_cf', 'Created')
					msg_dn_st="Sales Invoice  Return {0} delivery status is changed to {1}".format(self.name,'Created')
					frappe.msgprint(msg_dn_st,alert=1)
					create_returned_dn.add_comment('Comment', text=msg_dn_st)	

					msg="Return Delivery Note {0} is created. <br> Please check for correct item,qty and submit it".format(get_link_to_form("Delivery Note",returned_dn.name))
					frappe.msgprint(msg)
					self.add_comment('Comment', text=msg)		
		else:
			pass
			print('not connected...SI is directly returned')
		# SI is directly returned
			# dn_creted=make_delivery_note(self.name)
			# print('dn_creted',dn_creted)
			# if dn_creted:
			# 	dn=dn_creted.save(ignore_permissions=True)
			# 	frappe.db.set_value("Sales Invoice", self.name, 'delivery_status_cf', 'Created')
			# 	frappe.msgprint("Sales Invoice {0} delivery status is changed to {1}".format(self.name,'Created'),alert=1)
			# 	msg="Delivery Note {0} is auto created for <b>direct return.</b> No connected SI.<br> Please check for correct item,qty and submit it".format(get_link_to_form("Delivery Note",dn.name))
			# 	frappe.msgprint(msg)
			# 	self.add_comment('Comment', text=msg)				


def find_connected_delivery_notes(against_sales_invoice):
	connected_delivery_notes = frappe.db.sql("""SELECT DISTINCT(tdn.name)  
										  FROM `tabDelivery Note` as tdn inner join `tabDelivery Note Item` tdni on tdn.name =tdni.parent 
							where tdni.against_sales_invoice =%s and tdn.docstatus=1 limit 1""",(against_sales_invoice),as_dict=True,debug=1
	)
	return connected_delivery_notes

def update_delivery_status_cf_of_sales_invoice_from_dn(self,method):
	list_of_si=[]
	for item in self.items:
		if item.against_sales_invoice:
			if item.against_sales_invoice not in list_of_si:
				list_of_si.append(item.against_sales_invoice)
	if list_of_si and len(list_of_si)>0:
		for si in list_of_si:
			if self.docstatus==1:
				if self.is_return==1:
					# When DN returned is submited | Original_SI.dn_status='Received'
					frappe.db.set_value("Sales Invoice", si, 'delivery_status_cf', 'Received')
					msg="Sales Invoice {0} status is changed to {1}".format(si,'Received')
					frappe.msgprint(msg,alert=1)
					self.add_comment('Comment', text=msg)
					# When DN returned is submited | SI_return.dn_status='Delivered'
					return_against_list=frappe.db.get_all("Sales Invoice", filters={'return_against': si},fields=['name'],)
					if len(return_against_list)>0:
						frappe.db.set_value("Sales Invoice", return_against_list[0].name, 'delivery_status_cf', 'Delivered')
						msg_dn_st="Sales Invoice Return {0} status is changed to {1}".format(return_against_list[0].name,'Delivered')
						frappe.msgprint(msg_dn_st,alert=1)
						self.add_comment('Comment', text=msg_dn_st)						
						
				else:
					partial_found=False
					si_doc=frappe.get_doc('Sales Invoice',si)
					# delivered_qty
					for si_item in si_doc.items:
						if si_item.delivered_qty!=si_item.qty:
							partial_found=True
					if partial_found==True:
						frappe.db.set_value("Sales Invoice", si_doc.name, 'delivery_status_cf', 'Partial Delivered')
						msg="Sales Invoice {0} status is changed to {1}".format(si_doc.name,'Partial Delivered')
						frappe.msgprint(msg,alert=1)
						self.add_comment('Comment', text=msg)
					else:
						frappe.db.set_value("Sales Invoice",si_doc.name, 'delivery_status_cf', 'Delivered')
						msg="Sales Invoice {0} status is changed to {1}".format(si_doc.name,'Delivered')
						frappe.msgprint(msg,alert=1)
						self.add_comment('Comment', text=msg)
			elif self.docstatus==2:	
				# When DN returned is cancelled | Original_SI.dn_status='Cancelled'
				frappe.db.set_value("Sales Invoice", si, 'delivery_status_cf', 'Cancelled')
				msg="Sales Invoice {0} status is changed to {1}".format(si,'Cancelled')
				frappe.msgprint(msg,alert=1)
				self.add_comment('Comment', text=msg)
				# When DN returned is cancelled | SI_return.dn_status='Cancelled'
				return_against_list=frappe.db.get_all("Sales Invoice", filters={'return_against': si},fields=['name'],)
				if len(return_against_list)>0:
					frappe.db.set_value("Sales Invoice", return_against_list[0].name, 'delivery_status_cf', 'Cancelled')
					msg_dn_st="Sales Invoice Return {0} status is changed to {1}".format(return_against_list[0].name,'Cancelled')
					frappe.msgprint(msg_dn_st,alert=1)
					self.add_comment('Comment', text=msg_dn_st)				


def end_transit_in_stock_entry(self,method):
	if self.add_to_transit==1 and self.stock_entry_type=='Material Transfer' and self.items and self.items[0].material_request :
		end_transit=make_stock_in_entry(self.name)
		end_transit.from_warehouse=end_transit.get('items')[0].s_warehouse
		end_transit.to_warehouse=end_transit.get('items')[0].t_warehouse
		end_transit.save(ignore_permissions=True)
		frappe.msgprint("End Transit  {0}  is auto created in draft.".format(get_link_to_form('Stock Entry',end_transit.name)))

def after_install_run_patches():
	create_delivery_status_cf_in_sales_invoice()
	create_grace_child_table_in_customer()

def create_delivery_status_cf_in_sales_invoice():
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

def create_grace_child_table_in_customer():
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

def check_is(self,method):
	print(self.is_return,'===')

def check_qty_against_warehouse(self,method):
	if self.is_return==0 and self.update_stock==0:
		for item in self.items:
			is_stock_item = frappe.db.get_value('Item', item.item_code, 'is_stock_item')
			if is_stock_item==1 and item.qty > item.actual_qty:
				message=(_("Row {0} : item {1} has required qty {2} which is greater than warehouse qty {3}. <br> Please correct to proceed."
			   			.format(item.idx,item.item_name,item.qty,item.actual_qty)))
				frappe.throw(message)	

@frappe.whitelist()
def create_daily_customer_visit():
	today = getdate(nowdate())
	day=get_weekday(today)
	customer_list = frappe.db.get_all("Customer",
								   filters={"custom_single_day_visit":day,"disabled":0,"workflow_state":"Approved"},
								   fields=["name"])
	if len(customer_list)>0:
		for customer in customer_list:
			customer_visit_doc = frappe.new_doc("Customer Visit")
			customer_visit_doc.date = today
			customer_visit_doc.day = day
			customer_visit_doc.customer = customer.name
			customer_visit_doc.purpose_of_visit = ""
			customer_visit_doc.run_method("set_missing_values")
			customer_visit_doc.save(ignore_permissions=True)
			customer_visit_doc.add_comment("Comment", text='Customer Visit is created by system on {0}'.format(nowdate()))	
			customer_visit_doc.save(ignore_permissions=True)