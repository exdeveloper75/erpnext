from erpnext.setup.unisoft_currencies import restrict_currencies


def execute():
	restrict_currencies(delete_unused=True)
