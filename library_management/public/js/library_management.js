// Tags <body> with "library-dashboard" only while the Library Management
// workspace is open, so the matching CSS never leaks into other workspaces
// (this site also runs ERPNext/Avdaan workspaces that share the same DOM).
frappe.provide("library_management");

library_management.is_library_workspace = function () {
	const route = frappe.get_route() || [];
	const page = (route[1] === "private" ? route[2] : route[1]) || "";
	return page.replace(/-/g, " ").toLowerCase() === "library management";
};

library_management.sync_dashboard_class = function () {
	document.body.classList.toggle(
		"library-dashboard",
		library_management.is_library_workspace()
	);
};

$(document).on("app_ready", library_management.sync_dashboard_class);
frappe.router.on("change", library_management.sync_dashboard_class);
