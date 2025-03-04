// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Visit', {
	date: function(frm) {
		var a = new Date(frm.doc.date)
		var weekdays=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
		frm.set_value("day",weekdays[a.getDay()])
	},

	fetch_geolocation: async (frm) => {
		if (!navigator.geolocation) {
		  frappe.msgprint({
			message: __("Geolocation is not supported by your current browser"),
			title: __("Geolocation Error"),
			indicator: "red"
		  });
		//   hide_field(["geolocation"]);
		  return;
		}
		frappe.dom.freeze(__("Fetching your geolocation") + "...");
		navigator.geolocation.getCurrentPosition(
		  async (position) => {
			frm.set_value("latitude", position.coords.latitude);
			frm.set_value("longitude", position.coords.longitude);
			frappe.dom.unfreeze();
			// await frm.call("set_geolocation");
			
		  },
		  (error) => {
			frappe.dom.unfreeze();
			let msg = __("Unable to retrieve your location") + "<br><br>";
			if (error) {
			  msg += __("ERROR({0}): {1}", [error.code, error.message]);
			}
			frappe.msgprint({
			  message: msg,
			  title: __("Geolocation Error"),
			  indicator: "red"
			});
		  }
		);
		frm.save()
	  },
});


