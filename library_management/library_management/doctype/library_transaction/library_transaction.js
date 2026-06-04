frappe.ui.form.on('Library Transaction', {

    refresh(frm) {
        if (!frm.doc.date) {
            frm.set_value('date', frappe.datetime.get_today())
        }

        if (frm.doc.docstatus === 1) {
            if (frm.doc.type === "Issue") {
                frm.add_custom_button('Return Book', function() {
                    frappe.new_doc('Library Transaction', {
                        article: frm.doc.article,
                        library_member: frm.doc.library_member,
                        type: 'Return',
                        date: frappe.datetime.get_today()
                    })
                }, 'Actions')
            }

            if (frm.doc.due_date) {
                let due = frappe.datetime.str_to_obj(frm.doc.due_date)
                let today = new Date()
                let diff = Math.ceil((due - today) / (1000 * 60 * 60 * 24))

                if (diff < 0) {
                    frm.dashboard.set_headline(
                        `Book is ${Math.abs(diff)} days overdue!`, 'red'
                    )
                } else if (diff <= 3) {
                    frm.dashboard.set_headline(
                        `Due in ${diff} days!`, 'orange'
                    )
                } else {
                    frm.dashboard.set_headline(
                        `Due on ${frm.doc.due_date}`, 'green'
                    )
                }
            }
        }
    },

    article(frm) {
        if (frm.doc.article) {
            frappe.db.get_value('Article', frm.doc.article,
                ['status', 'author'],
                function(data) {
                    if (data) {
                        if (data.status === 'Available') {
                            frappe.show_alert({
                                message: `"${frm.doc.article}" is Available!`,
                                indicator: 'green'
                            })
                        } else {
                            frappe.show_alert({
                                message: `"${frm.doc.article}" is Already Issued!`,
                                indicator: 'red'
                            })
                        }
                        frm.set_intro(
                            `Author: ${data.author} | Status: ${data.status}`,
                            data.status === 'Available' ? 'green' : 'red'
                        )
                    }
                }
            )
        }
    },

    library_member(frm) {
        if (frm.doc.library_member) {
            frappe.db.get_value(
                'Library Member',
                frm.doc.library_member,
                ['first_name', 'last_name', 'email_address'],
                function(data) {
                    if (data) {
                        let full_name = data.first_name + ' ' + (data.last_name || '')
                        frappe.show_alert({
                            message: `Member: ${full_name}`,
                            indicator: 'blue'
                        })
                        frm.set_intro(
                            `Member: ${full_name} | Email: ${data.email_address || 'N/A'}`,
                            'blue'
                        )
                    }
                }
            )

            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Library Membership',
                    filters: {
                        library_member: frm.doc.library_member,
                        from_date: ['<=', frappe.datetime.get_today()],
                        to_date: ['>=', frappe.datetime.get_today()]
                    },
                    fields: ['name', 'to_date']
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frappe.show_alert({
                            message: `Valid Membership till ${r.message[0].to_date}`,
                            indicator: 'green'
                        })
                    } else {
                        frappe.show_alert({
                            message: `No Active Membership!`,
                            indicator: 'red'
                        })
                    }
                }
            })
        }
    },

    type(frm) {
        if (frm.doc.type === 'Issue') {
            frm.set_intro('Issuing a book to member', 'blue')
        } else if (frm.doc.type === 'Return') {
            frm.set_intro('Returning a book from member', 'orange')
        }
    }

})
