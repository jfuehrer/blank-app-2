# this module include common utilities like csv handling (load_data, validate_csv_columns)and simliar functions to avoid code reptition
import pandas as pd
import requests

# Define the API endpoint - this is the financials. Need to confirm with Stuti if the reports api endpoint is for us and when can we use it.
url = "http://scvp.mitre.org:8000/docs#/Financials/integrated_financials_api_v2_financials_get"

'''
# Optional: Add headers if required by the API (e.g., authentication tokens)
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # Replace YOUR_ACCESS_TOKEN with your actual token
    "Content-Type": "application/json"
}
'''

def fetch_vendor_data(vendor_id, base_url="http://scvp.mitre.org:8000/docs#/Financials/integrated_financials_api_v2_financials_get"):
    '''aquire data from api
    :param vendor_id (confirm will we use vendor, company name, ticker?)
    :return vendor data dict or raises error
    '''
    url = f"{base_url}/{vendor_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetchinv endor data: {e}")
        raise