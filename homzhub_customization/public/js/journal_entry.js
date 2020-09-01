frappe.ui.form.on('Journal Entry', {
    refresh: function(frm) {
        frm.add_custom_button('get expense entries', () => {
            let table_values = [];
            var d = new frappe.ui.Dialog({
                'fields': [
                    {fieldname: 'from_date',label:'From Date', fieldtype: 'Date', default: frappe.datetime.nowdate()},
                    {fieldname: 'to_date',label:'To Date', fieldtype: 'Date', default: frappe.datetime.nowdate()},
                    {fieldname:'employee',label:'Employee',fieldtype:'Link',options:'Employee'},
                    {fieldtype: "Button",label: __("Get Data"),
                        click: function() {
                            d.set_value('table',[])
                            while(table_values.length > 0) {
                                table_values.pop();
                            }
                            d.fields_dict.expense_table.grid.refresh();
                            frappe.call({
                                method: 'homzhub_customization.homzhub_customization.doctype.employee.execute',
                                args: {
                                    emp:d.get_value('employee'),
                                    from_date:d.get_value('from_date'),
                                    to_date:d.get_value('to_date')
                                },
                                callback: (r) => {
                                    $.each(r.message || [], function (i, v) {
                                        table_values.push ({
                                            'employee_name':v.employee_name,
                                            'posting_date':v.posting_date,
                                            'expense_no':v.name,
                                            'total_amount':v.total_claimed_amount
                                        });
                                        d.fields_dict.expense_table.grid.refresh();
                                    })
                                }
                            });
                        }
                    },
                    {fieldname:'expense_table',label:'Expense Table',fieldtype:'Table',options:'Sales Invoice Item',
                    fields: [
                        {
                            fieldtype:'Link',
                            fieldname:'expense_no',
                            label: __('Expense No'),
                            options:'Expense Claim',
                            in_list_view:1
                        },
                        {
                            fieldtype: 'Date', 
                            fieldname: 'posting_date',
                            label:'Posting Date', 
                            in_list_view:1,
                            default: frappe.datetime.nowdate()
                        },
                        {
                            fieldtype:'Data',
                            fieldname:'employee_name',
                            label: __('Employee Name'),
                            in_list_view:1
                        },
                        {
                            fieldtype:'Data',
                            fieldname:'total_amount',
                            label: __('Total Amount'),
                            in_list_view:1
                        },
                    ],
                    data: table_values,
                    in_place_edit: true,
                    get_data: function() {
                        return table_values;
                    }
                    }
                ],
                primary_action: function(){
                frm.set_value('accounts',[])
                frm.refresh_field("accounts")
                Object.values(d.get_value('expense_table')).forEach(i=>{
                    var acc = frm.add_child("accounts")
                    acc.account="Creditors - HAPL"
                    acc.party_type="Employee"
                    acc.party=d.get_value('employee')
                    acc.debit_in_account_currency=i.total_amount
                    acc.reference_type="Expense Claim"
                    acc.reference_name=i.expense_no
                    })
                    frm.refresh_field("accounts")
                    d.hide();
                    show_alert({
                        message: __('Successfully Done'),
                        indicator: 'green'
                    });
                },
                primary_action_label: __('Insert')
               
            });
            d.show();
            
        })
    },
    
})

