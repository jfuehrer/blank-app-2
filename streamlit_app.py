import streamlit as st
from utils import fetch_vendor_data
from score_calculator import calculate_scores

vendor_id = st.sidebar.text_input("enter Vendor ID", "company name here")
vendor_data = None  # Initialize vendor_data with a default value
results = {}
if vendor_id:
    try:
        vendor_data = fetch_vendor_data(vendor_id)
        results = calculate_scores(vendor_data)
        st.write("### Vendor Risk Reliability Report")
        st.json(results)
    except Exception as e:
        st.error(f"Error: {e}")
        
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
results = calculate_scores(vendor_data)

# Display results in streamlit
st.subheader("Score Results")
for key, value in results.items():
    st.write(f"**{key}**: {value}")