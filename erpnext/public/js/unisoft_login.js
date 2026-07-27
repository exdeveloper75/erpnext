frappe.ready(function () {
	if (!document.body || document.body.getAttribute("data-path") !== "login") {
		return;
	}
	const title = document.querySelector(".for-login .page-card-head-text h4");
	if (title && /sign in/i.test(title.textContent || "")) {
		title.textContent = "Sign in to MezanErp";
	}
	const subtitle = document.querySelector(".for-login .page-card-subtitle");
	if (subtitle) {
		subtitle.textContent = "Welcome back. Use your account to continue.";
	}
	// Replace default ERPNext logo with Mezan M logo
	document.querySelectorAll(".for-login img, .page-card img, .app-logo").forEach((img) => {
		img.src = "/assets/erpnext/images/mezan-logo.svg";
		img.alt = "MezanErp";
		img.style.borderRadius = "10px";
	});
});
