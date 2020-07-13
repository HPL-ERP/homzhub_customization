frappe.listview_settings['Rent Transaction'] = {
	get_indicator: function(doc) {
		if(doc.status === 'Rent Received') {
			return [__("Rent Received"), "green"];
		} else if(doc.status === 'Rent Transffered') {
			return [__("Rent Transffered"), "green"];
		} else if(doc.status === 'Draft') {
			return [__("Draft"), "red"];
		} 
	}
};