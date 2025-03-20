import streamlit as st
from score_calculator import calculate_scores

# sample vendor data
vendor_data_example = {
    'Vendor': 'Palo Alto',
    'Altman_Z': 3,
    'DTE': 2.1,
    'DTI': 3.1,
    'ROA': .2,
    'ROE': .2,
    'Non-Fulfillment': 5,
    'Compliance': 2,
    'Adminstrative': 3,
    'awards': [
        {'type': 'prime_contract', 'amount': 6_278_000},
        {'type': 'prime_assistance', 'amount': 0},
        {'type': 'sub_contract', 'amount': 1_000_000}
    ],
    'competition_percentage': 3,
    'agency_count': 2,
    'sub_agency_count': 3,
    'countries_data': [
        {
             'country': 'Canada',
             'job_counts_low': 100,
             'job_counts_moderate': 100,
             'job_counts_high': 25,   
        },
        #{
         #   'country': 'India',
           # 'job_counts_low': 5,
           # 'job_counts_moderate': 10,
            #'job_counts_high': 15,  
        #}
    ],
    'visa_certified_count': 100,
    'visa_denied_count': 33,
    'visa_withdrawn_count': 21,
    'visa_certified_expired_count': 1,
    'visa_unspecified_count': 11,
}

# title for streamlit app
st.title("Vendor Risk Reliability Score Report")

# Calculate scores for the example data
results = calculate_scores(vendor_data_example)

# Display results in streamlit
st.subheader("Score Results")
for key, value in results.items():
    st.write(f"**{key}**: {value}")