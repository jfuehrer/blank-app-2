import streamlit as st
from score_calculator import calculate_scores

# sample vendor data vs calling csv or api. just for testing purposes
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

# Sidebar Input Section
st.sidebar.header("Tailor Risk Strategies")

# Financial Risk Weight Slider
financial_weight = st.sidebar.slider(
    label="Financial Stability Weight",
    min_value=0.0,
    max_value=1.0,
    value=0.35,         # default value from RISK_WEIGHTS
    step=0.05,
    help="adjust financial risk weighting due to changes in strategy"
)

# Past Contract Performance Slider
past_performance_weight = st.sidebar.slider(
    label="Past Contract Performance Weight",
    min_value=0.0,
    max_value=1.0,
    value=0.20,         # default value from RISK_WEIGHTS
    step=0.05,
    help="adjust past contract performance risk weighting due to changes in strategy"
)

# Federal Contract Diversity Weight Slider
federal_contract_weight = st.sidebar.slider(
    label="Federal Contract Diversity Weight",
    min_value=0.0,
    max_value=1.0,
    value=0.10,         # default value from RISK_WEIGHTS
    step=0.05,
    help="adjust federal contract diversity risk weighting due to changes in strategy"
)

# Foreign Labor Risk Weight Slider
foreign_labor_risk = st.sidebar.slider(
    label="Foreign Labor Risk Weight",
    min_value=0.0,
    max_value=1.0,
    value=0.30,         # default value from RISK_WEIGHTS
    step=0.05,
    help="adjust foreign labor risk weighting due to changes in strategy"
)

# Calculate scores for the example data
results = calculate_scores(vendor_data_example)

# Display results in streamlit
st.subheader("Score Results")
for key, value in results.items():
    st.write(f"**{key}**: {value}")


# concept, have nobs to adjust risk weighting based on changing risk strategy of an organization. Current iteration the nobs adjust the scores (v.1) Need to figure how to pass to calculate_scores below
'''

#need to recalculate weights based on slide (optional would be auto-adjust others to sum of 1.0)

custom_weights = {
    'financial_stability': financial_weight,
    'past_performance': past_performance_weight,
    'federal_contract': federal_contract_weight,
    'foreign_labor_risk': foreign_labor_risk
}

#I still need to pass to calculate_scores; the following are how

vrrs_score = (
    financial_stability_score * custom_weights['financial_stability'] +
    past_performance_score * custom_weights['past_performance'] +
    federal_contract_score * custom_weights['federal_contract'] +
    foreign_labor_score * custom_weights['foreign_labor_risk']
)


'''