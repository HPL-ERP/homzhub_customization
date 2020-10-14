frappe.ui.form.on('Task', {
	onload: function(frm) {
		if (frm.doc.project){
            frappe.call({
                method:
                "homzhub_customization.homzhub_customization.doctype.task.fetch_owner_and_tenant_table",
                args: {
                    docname: frm.doc.project      
                },
                callback: function (data) {
                   frm.set_value("owner_list",[])
                   frm.set_value("tenant_list",[])
                    $.each(data.message[0] || [], function (i, v) {
                        var d = cur_frm.add_child("owner_list")
                        d.prop_owner=v.prop_owner
                        d.owner_name=v.owner_name
                    })
                    cur_frm.refresh_field("owner_list")

                    $.each(data.message[1] || [], function (i, v) {
                        var d = cur_frm.add_child("tenant_list")
                        d.tenant=v.tenant
                        d.tenant_name=v.tenant_name
                    })
                    cur_frm.refresh_field("tenant_list")
                }
            })
        }
	},
})