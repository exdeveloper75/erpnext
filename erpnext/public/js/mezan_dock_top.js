/**
 * Mezan experiment: enable top horizontal workspace dock.
 * Adds body.mezan-top-dock once and keeps Mezan ERP beside the logo.
 *
 * Intentionally quiet: no body-wide MutationObserver (that re-ran on every
 * click/tooltip and caused toolbar flicker).
 *
 * ROLLBACK: remove this file from hooks.py app_include_js and undeploy the asset.
 */
(function () {
	let logoObserver = null;

	function getAppTitle() {
		try {
			const apps = (window.frappe && frappe.boot && frappe.boot.app_data) || [];
			const erpnext = apps.find((a) => a.app_name === "erpnext");
			if (erpnext && erpnext.app_title) {
				return erpnext.app_title;
			}
			const preferred = apps.find(
				(a) =>
					a.app_name &&
					a.app_name !== "frappe" &&
					a.app_title &&
					a.app_title !== "Framework" &&
					!/frappe framework/i.test(a.app_title)
			);
			if (preferred) {
				return preferred.app_title;
			}
			return "Mezan ERP";
		} catch (e) {
			return "Mezan ERP";
		}
	}

	function ensureAppNameBesideLogo() {
		const logo = document.querySelector(".workspace-dock .workspace-dock-logo");
		if (!logo) {
			return false;
		}

		logo.classList.add("mezan-dock-logo");
		const link = logo.querySelector("a");
		if (link) {
			link.classList.add("mezan-dock-brand-link");
			link.querySelectorAll(".mezan-dock-app-name, span").forEach((el) => el.remove());
		}

		let titleEl = null;
		for (let i = 0; i < logo.children.length; i++) {
			if (logo.children[i].classList.contains("mezan-dock-app-name")) {
				titleEl = logo.children[i];
				break;
			}
		}

		if (!titleEl) {
			titleEl = document.createElement("span");
			titleEl.className = "mezan-dock-app-name";
			if (link && link.nextSibling) {
				logo.insertBefore(titleEl, link.nextSibling);
			} else {
				logo.appendChild(titleEl);
			}
		}

		const title = getAppTitle();
		const desiredHtml = formatAppTitleHtml(title);
		if (titleEl.getAttribute("data-title") !== title) {
			titleEl.setAttribute("data-title", title);
			titleEl.innerHTML = desiredHtml;
		}
		return true;
	}

	function formatAppTitleHtml(title) {
		const safe = String(title || "Mezan ERP");
		// Color only the trailing "ERP" word (e.g. "Mezan ERP")
		if (/\bERP\b/i.test(safe)) {
			return safe.replace(
				/\b(ERP)\b/i,
				'<span class="mezan-dock-app-name-erp">$1</span>'
			);
		}
		return safe;
	}

	function watchLogo() {
		const logo = document.querySelector(".workspace-dock .workspace-dock-logo");
		if (!logo) {
			return;
		}
		if (logoObserver) {
			logoObserver.disconnect();
		}
		// Only watch the logo node: Frappe empties it on refresh(); we re-add the title.
		logoObserver = new MutationObserver(function () {
			ensureAppNameBesideLogo();
		});
		logoObserver.observe(logo, { childList: true });
	}

	function isDockUserParent(parent) {
		try {
			const el = window.jQuery ? $(parent)[0] : parent && parent.nodeType ? parent : null;
			return Boolean(el && el.closest && el.closest(".workspace-dock"));
		} catch (e) {
			return false;
		}
	}

	function fixDockUserMenus() {
		try {
			const map = (window.frappe && frappe.menu_map) || {};
			Object.keys(map).forEach(function (key) {
				const menu = map[key];
				if (!menu || !isDockUserParent(menu.parent || (menu.opts && menu.opts.parent))) {
					return;
				}
				// Top bar avatar: open downward and align to the right edge
				menu.open_on_top = false;
				menu.open_on_left = true;
				if (menu.opts) {
					menu.opts.open_on_top = false;
					menu.opts.open_on_left = true;
				}
			});
		} catch (e) {
			/* ignore */
		}
	}

	function patchCreateMenu() {
		if (!window.frappe || !frappe.ui || typeof frappe.ui.create_menu !== "function") {
			return false;
		}
		if (frappe.ui.create_menu.__mezan_patched) {
			return true;
		}
		const original = frappe.ui.create_menu;
		frappe.ui.create_menu = function (opts) {
			opts = opts || {};
			if (isDockUserParent(opts.parent)) {
				opts = Object.assign({}, opts, {
					open_on_top: false,
					open_on_left: true,
				});
			}
			const menu = original(opts);
			fixDockUserMenus();
			return menu;
		};
		frappe.ui.create_menu.__mezan_patched = true;
		return true;
	}

	function boot() {
		if (!document.body) {
			return;
		}
		document.body.classList.add("mezan-top-dock");
		patchCreateMenu();
		fixDockUserMenus();
		ensureAppNameBesideLogo();
		watchLogo();
	}

	function start() {
		boot();

		// Dock / menus may appear after first paint — poll briefly, then stop.
		let tries = 0;
		const timer = setInterval(function () {
			tries += 1;
			patchCreateMenu();
			fixDockUserMenus();
			ensureAppNameBesideLogo();
			watchLogo();
			if (
				(document.querySelector(".workspace-dock .workspace-dock-logo") &&
					frappe.menu_map &&
					Object.keys(frappe.menu_map).length) ||
				tries > 40
			) {
				clearInterval(timer);
				patchCreateMenu();
				fixDockUserMenus();
			}
		}, 250);

		// After route/workspace changes, logo may be rebuilt — light hook only.
		document.addEventListener("page-change", function () {
			setTimeout(function () {
				ensureAppNameBesideLogo();
				watchLogo();
				fixDockUserMenus();
			}, 0);
		});
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
