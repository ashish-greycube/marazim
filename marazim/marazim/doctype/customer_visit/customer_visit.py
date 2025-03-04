# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomerVisit(Document):
	@frappe.whitelist()
	def set_geolocation(self):
		# if not frappe.db.get_single_value("HR Settings", "allow_geolocation_tracking"):
		# 	return

		if not (self.latitude and self.longitude):
			return

		self.geolocation = frappe.json.dumps(
			{
				"type": "FeatureCollection",
				"features": [
					{
						"type": "Feature",
						"properties": {},
						# geojson needs coordinates in reverse order: long, lat instead of lat, long
						"geometry": {"type": "Point", "coordinates": [self.longitude, self.latitude]},
					}
				],
			}
		)
