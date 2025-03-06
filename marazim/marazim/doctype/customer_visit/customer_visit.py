# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from geopy import distance

class CustomerVisit(Document):
	def on_submit(self):
		self.validate_purpose_of_visit()
		self.validate_distance_from_current_location()

	def validate_purpose_of_visit(self):
		if self.purpose_of_visit == "" or self.purpose_of_visit == None:
			frappe.throw(_("Please select Purpose of Visit before submit this form"))
	def validate_distance_from_current_location(self):
		if self.latitude and self.longitude:
			current_latitude, current_longitude = self.latitude, self.longitude
			current_geo_location = (current_latitude, current_longitude)
			
			customer_latitude, customer_longitude = frappe.db.get_value("Customer",{"name":self.customer},["custom_office_latitude","custom_office_longitude"])
			customer_geo_location = (customer_latitude, customer_longitude)
			print(current_geo_location,customer_geo_location,"++++++")
			if customer_latitude and customer_longitude:
				distance_between_two_points = distance.distance(current_geo_location, customer_geo_location).m
				print(distance_between_two_points,"----------------------")

				distance_limit = frappe.db.get_single_value("Marazim Settings","limit_for_visitor")
				if distance_limit:
					if distance_between_two_points > distance_limit :
						frappe.throw(_("You cannot Submit because current distance is greater than expected distance<br>Current : Latitude - {0}, Longitude - {1} <br>Company : Latitude - {2}, Longitude - {3} <br>Expected Distance : {4} <br>Current Distance : {5}".format(current_latitude, current_longitude,customer_latitude,customer_longitude,distance_limit,distance_between_two_points)))
					else :
						frappe.msgprint(_("Current : Latitude - {0}, Longitude - {1} <br>Company : Latitude - {2}, Longitude - {3} <br>Expected Distance : {4} <br>Current Distance : {5}".format(current_latitude, current_longitude,customer_latitude,customer_longitude,distance_limit,distance_between_two_points)),alert=True)
				else :
					frappe.throw(_("Please set Limit for visitor in {0}".format(get_link_to_form("Marazim Settings","Marazim Settings"))))
			else :
				frappe.throw(_("Please set Latitude and Longitude in Customer {0}".format(get_link_to_form("Customer",self.customer))))
		else :
			frappe.throw(_("Latitude and Longitude Must be greater than 0.0"))