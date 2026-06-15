import frappe
from frappe.desk.doctype.number_card.number_card import get_result
import traceback

def run():
    doc = frappe._dict({
        'function': 'Count',
        'document_type': 'Books Reservation',
        'aggregate_function_based_on': '',
        'parent_document_type': ''
    })
    filters = None
    to_date = '2026-06-11'
    
    print(f"Filters before call: {filters} ({type(filters)})")
    
    try:
        get_result(doc, filters, to_date)
        print("Success with None")
    except Exception:
        traceback.print_exc()
        
    filters = '[]'
    print(f"Filters before call: {filters} ({type(filters)})")
    try:
        get_result(doc, filters, to_date)
        print("Success with '[]'")
    except Exception:
        traceback.print_exc()
        
    filters = '{}'
    print(f"Filters before call: {filters} ({type(filters)})")
    try:
        get_result(doc, filters, to_date)
        print("Success with '{}'")
    except Exception:
        traceback.print_exc()
