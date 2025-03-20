import streamlit as st
from score_calculator import calculate_scores

# sample vendor data
vendor_data_example = {
    'Vendor': 'Palo Alto',
    'Altman_Z': 1.65,
    'DTE': 1.1,
    'DTI': 1.9,
    'ROA': -0.34,
    'ROE': -0.81,
    'Non-Fulfillment': 0,
    'Compliance': 0,
    'Adminstrative': 0,
    'awards': [
        {'type': 'prime_contract', 'amount': 6_278_000},
        {'type': 'prime_assistance', 'amount': 0},
        {'type': 'sub_contract', 'amount': 1_000_000}
    ],
    'competition_percentage': 3,
    'agency_count': 2,
    'sub_agency_count': 3,
    'foreign_labor_percentage': 1,
    'countries_data': [
        {
             'country': 'Canada',
             'job_counts_low': 0,
             'job_counts_moderate': 1,
             'job_counts_high': 0,   
        },
        #{
         #   'country': 'India',
           # 'job_counts_low': 5,
           # 'job_counts_moderate': 10,
            #'job_counts_high': 15,  
        #}
    ],
    'visa_certified_count': 1,
    'visa_denied_count': 0,
    'visa_withdrawn_count': 0,
    'visa_certified_expired_count': 0,
    'visa_unspecified_count': 0,
    'certified_trend': 10,
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