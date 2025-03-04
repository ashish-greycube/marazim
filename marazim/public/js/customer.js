frappe.ui.form.on("Customer",{
    custom_set_location: function name(frm) {
        let lat_long = /\/\@(.*),(.*),/.exec(frm.doc.custom_client_location_url);
        console.log(lat_long,"---------------",lat_long[1],lat_long[2])
        frm.set_value("custom_office_latitude",lat_long[1])
        frm.set_value("custom_office_longitude",lat_long[2])
        frm.save()
      },
})