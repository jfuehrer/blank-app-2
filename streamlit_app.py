import streamlit as st
from score_calculator import calculate_scores

# sample vendor data
vendor_data_example = {
    'Vendor': 'Vendor A',
    'Altman_Z': 3.5,
    'DTE': 1.2,
    'DTI': 0.8,
    'ROA': 0.15,
    'ROE': 0.12,
    'Non-Fulfillment': 1,
    'Compliance': 0,
    'Adminstrative': 2,
    'Agency Count': 4,
    'Sub Agency Count': 3,
    'Growth Rate': 7,
    'No Competition Percentage': 20,
    'foreign_labor_percentage': 15,
    'countries_data': [
        {
             'country': 'Russia',
             'job_counts_low': 10,
             'job_counts_moderate': 20,
             'job_counts_high': 5,   
        },
        {
            'country': 'India',
            'job_counts_low': 5,
            'job_counts_moderate': 10,
            'job_counts_high': 15,  
        }
    ],
    'visa_certified_count': 30,
    'visa_denied_count': 10,
    'visa_withdrawn_count': 5,
    'visa_certified_expired_count': 2,
    'visa_unspecified_count': 1,
    'certified_trend': 6,
    'denied_withdrawn_trend': 10
}

# title for streamlit app
st.title("Vendor Risk Reliability Score Report")

# Calculate scores for the example data
results = calculate_scores(vendor_data_example)

# Display results in streamlit
st.subheader("Score Results")
for key, value in results.items():
    st.write(f"**{key}**: {value}")