frappe.ui.form.on('Sales Invoice', {
    is_return: function (frm) {
        if (frm.doc.is_return==1 && (frm.doc.return_against==undefined || frm.doc.return_against=='')) {
            frm.set_value('update_stock', 1)
        }
    },
    validate: function (frm) {
        frm.trigger('set_customer_balance');
    },

	customer: function (frm) {
		frm.trigger('set_customer_balance');
	},
    set_customer_balance: function (frm) {
		var customer = frm.doc.customer
		var posting_date=frm.doc.posting_date
		if (customer && posting_date) {
			return frappe.call({
				method: 'erpnext.accounts.utils.get_balance_on',
				args: {
					'party_type': 'Customer',
					'party': customer,
					'date': posting_date,
					'company': frm.doc.company
				},
				callback: (r) => {
					console.log('frm.doc.docstatus',frm.doc.docstatus)
					var base_grand_total=frm.doc.base_grand_total
					var status=frm.doc.docstatus
					if (base_grand_total && (status==0)) {
						var balance_with_si=base_grand_total+r.message
						frm.set_value('custom_customer_balance',balance_with_si)
					} else {
						frm.set_value('custom_customer_balance', r.message)
					}
				},
				error: (r) => {
					console.log('error', r)
				}
			})
		}
	},
})