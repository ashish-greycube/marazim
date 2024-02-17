import frappe
from erpnext.selling.doctype.customer.customer import get_credit_limit, get_customer_outstanding
from frappe.utils import add_days,getdate,flt
from frappe import _, msgprint, throw
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from frappe.utils import get_link_to_form
from erpnext.stock.doctype.stock_entry.stock_entry import make_stock_in_entry
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_return

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
	if self.is_return==0:
		dn_creted=make_delivery_note(self.name)
		print('dn_creted',dn_creted)
		if dn_creted:
			dn=dn_creted.save(ignore_permissions=True)
			frappe.db.set_value("Sales Invoice", self.name, 'delivery_status_cf', 'Created')
			frappe.msgprint("Sales Invoice {0} status is changed to {1}".format(self.name,'Created'),alert=1)
			msg="Delivery Note {0} is auto created<br> Please ensure DN is submitted before SI return is done".format(get_link_to_form("Delivery Note",dn.name))
			frappe.msgprint(msg)
			self.add_comment('Comment', text=msg)
	elif self.is_return==1:
		# find the DN created and submitted, and return them in draft stage
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
					msg="Return Delivery Note {0} is created. <br> Please check for correct item,qty and submit it".format(get_link_to_form("Delivery Note",returned_dn.name))
					frappe.msgprint(msg)
					self.add_comment('Comment', text=msg)					



def find_connected_delivery_notes(against_sales_invoice):
	connected_delivery_notes = frappe.db.sql("""SELECT UNIQUE(tdn.name)  
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
				# is_return_si=frappe.db.get_value("Sales Invoice", si, 'is_return')
				if self.is_return==1:
					frappe.db.set_value("Sales Invoice", si, 'delivery_status_cf', 'Received')
					frappe.msgprint("Sales Invoice {0} status is changed to {1}".format(si,'Received'),alert=1)
				else:
					partial_found=False
					si_doc=frappe.get_doc('Sales Invoice',si)
					# delivered_qty
					for si_item in si_doc.items:
						if si_item.delivered_qty!=si_item.qty:
							partial_found=True
					if partial_found==True:
						frappe.db.set_value("Sales Invoice", si_doc.name, 'delivery_status_cf', 'Partial Delivered')
						frappe.msgprint("Sales Invoice {0} status is changed to {1}".format(si_doc.name,'Partial Delivered'),alert=1)
					else:
						frappe.db.set_value("Sales Invoice",si_doc.name, 'delivery_status_cf', 'Delivered')
						frappe.msgprint("Sales Invoice {0} status is changed to {1}".format(si_doc.name,'Delivered'),alert=1)
			elif self.docstatus==2:	
				frappe.db.set_value("Sales Invoice", si, 'delivery_status_cf', 'Cancelled')
				frappe.msgprint("Sales Invoice {0} status is changed to {1}".format(si,'Cancelled'),alert=1)


def end_transit_in_stock_entry(self,method):
	if self.add_to_transit==1 and self.stock_entry_type=='Material Transfer' and self.items and self.items[0].material_request :
		end_transit=make_stock_in_entry(self.name)
		end_transit.save(ignore_permissions=True)
		frappe.msgprint("End Transit  {0}  is auto created in draft.".format(get_link_to_form('Stock Entry',end_transit.name)))