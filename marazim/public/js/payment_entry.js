frappe.ui.form.on('Payment Entry', {
    // paid_amount: function (frm) {
    //     if (frm.doc.payment_type == 'Receive' && frm.doc.party_type == 'Customer' && frm.doc.paid_amount) {
    //         let filters = {
    //             "to_posting_date": frappe.datetime.get_today(),
    //             "outstanding_amt_greater_than": 0,
    //             "outstanding_amt_less_than": 0,
    //             "allocate_payment_amount": 1
    //         }
    //         let get_outstanding_invoices = true
    //         let get_orders_to_be_billed = false
    //         frm.events.get_outstanding_documents(frm, filters, get_outstanding_invoices, get_orders_to_be_billed);
    //     }
    // }
})