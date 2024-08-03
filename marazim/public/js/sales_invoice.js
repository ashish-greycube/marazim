frappe.ui.form.on('Sales Invoice', {
    is_return: function (frm) {
        if (frm.doc.is_return==1 && (frm.doc.return_against==undefined || frm.doc.return_against=='')) {
            frm.set_value('update_stock', 1)
        }
    }
})