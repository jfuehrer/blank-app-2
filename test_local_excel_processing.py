import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import tempfile

from utils import process_excel_report
from score_calculator import calculate_scores, DEFAULT_RISK_WEIGHTS

def main():
    st.title("Comprehensive Excel Report Processing")
    st.write("Process Excel reports with multiple sheets for all risk categories.")
    excel_processing_tab()

def excel_processing_tab():
    """Excel report processing tab content"""

    # Initialize session state variables
    if 'excel_processed' not in st.session_state:
        st.session_state.excel_processed = False
    if 'excel_vendor_data' not in st.session_state:
        st.session_state.excel_vendor_data = None
    if 'excel_results' not in st.session_state:
        st.session_state.excel_results = None
    if 'excel_company_name' not in st.session_state:
        st.session_state.excel_company_name = None
    if 'excel_risk_category' not in st.session_state:
        st.session_state.excel_risk_category = "Financial Stability"

    # Add a reset button
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Reset", key="reset_excel"):
            st.session_state.excel_processed = False
            st.session_state.excel_vendor_data = None
            st.session_state.excel_results = None 
            st.session_state.excel_company_name = None
            st.session_state.excel_risk_category = "Financial Stability"
            st.rerun()

    with col1:
        if not st.session_state.excel_processed:
            st.subheader("Select Excel Report")
        else:
            st.subheader(f"Report Analysis for {st.session_state.excel_company_name}")

    if not st.session_state.excel_processed:
        file_selection_method = st.radio(
            "Select Excel Report Source",
            ["Upload a file", "Use sample file"],
            index=1
        )

        excel_file = None
        company_name = None

        if file_selection_method == "Upload a file":
            uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    excel_file = tmp_file.name

                company_name = st.text_input("Enter Company Name", 
                                          value=uploaded_file.name.split('.')[0] if '.' in uploaded_file.name else uploaded_file.name)

        else:
            sample_file = "Sample Report.xlsx"
            excel_file = sample_file
            company_name = "Sample Company"

            if os.path.exists(excel_file):
                st.success(f"Using sample file: {sample_file}")
            else:
                st.error(f"Sample file not found: {excel_file}")
                excel_file = None

        process_button = st.button("Process Excel Report")

        if process_button and excel_file and company_name:
            with st.spinner(f"Processing Excel report for {company_name}..."):
                vendor_data = process_excel_report(excel_file, company_name)

                if file_selection_method == "Upload a file" and os.path.exists(excel_file):
                    try:
                        os.unlink(excel_file)
                    except OSError as e:
                        st.error(f"Error deleting temporary file: {e}")

                if vendor_data:
                    st.session_state.excel_processed = True
                    st.session_state.excel_vendor_data = vendor_data
                    st.session_state.excel_company_name = company_name

                    with st.spinner("Calculating risk scores..."):
                        results = calculate_scores(vendor_data, DEFAULT_RISK_WEIGHTS)
                        st.session_state.excel_results = results

                    st.success("Successfully processed the Excel report!")
                    st.rerun()
                else:
                    st.error("Failed to process the Excel report. Please check if the file is in the expected format.")

    else:
        vendor_data = st.session_state.excel_vendor_data
        results = st.session_state.excel_results
        company_name = st.session_state.excel_company_name

        with st.expander("Raw Vendor Data"):
            st.json(vendor_data)

        if results:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(f"{company_name} Risk Assessment")
                st.write(f"Overall Risk Category: {results['risk_category']}")

            with col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=results["vrrs_score"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "VRRS Score"},
                    gauge={
                        'axis': {'range': [1, 10], 'tickvals': [1, 2.5, 5, 7.5, 10]},
                        'steps': [
                            {'range': [1, 3], 'color': "green"},
                            {'range': [3, 5], 'color': "lightgreen"},
                            {'range': [5, 7], 'color': "yellow"},
                            {'range': [7, 8.5], 'color': "orange"},
                            {'range': [8.5, 10], 'color': "red"},
                        ]
                    }
                ))
                fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Component Scores")
            score_cols = st.columns(3)

            with score_cols[0]:
                st.metric("Financial Stability", f"{results['financial_stability_score']:.2f}/10", 
                        results['financial_stability_category'])
                st.metric("Foreign Labor Risk", f"{results['foreign_labor_score']:.2f}/10", 
                        results['foreign_labor_category'])

            with score_cols[1]:
                st.metric("Past Performance", f"{results['past_performance_score']:.2f}/10", 
                        results['past_performance_category'])
                st.metric("Sanctions Risk", f"{results.get('sanctions_score', 0):.2f}/10", 
                        results.get('sanctions_category', 'Unknown'))

            with score_cols[2]:
                st.metric("Federal Contract", f"{results['federal_contract_score']:.2f}/10", 
                        results['federal_contract_category'])

            # Display the risk interpretation
            st.subheader("Risk Interpretation")
            st.markdown(results["interpretation"])

            # Display risk category heatmap
            st.subheader("Risk Category Heat Map")
            selected_risk_category = st.selectbox(
                "Select Risk Category",
                ["Financial Stability", "Past Performance", "Federal Contract", "Foreign Labor", "Sanctions Risk"],
                index=0
            )

            # Get the appropriate risk factors and scores based on selected category
            risk_factors = []
            scores = []

            if selected_risk_category == "Financial Stability":
                risk_factors = ["Altman Z-Score", "Debt-to-Equity", "Debt-to-Income", "Return on Assets", "Return on Equity"]
                fin_details = results.get("financial_details", {})
                scores = [
                    fin_details.get("altman_z_score_normalized", 5),
                    fin_details.get("debt_to_equity_normalized", 5),
                    fin_details.get("debt_to_income_normalized", 5),
                    fin_details.get("return_on_assets_normalized", 5),
                    fin_details.get("return_on_equity_normalized", 5)
                ]
            elif selected_risk_category == "Past Performance":
                risk_factors = ["Non-Fulfillment", "Compliance", "Administrative"]
                perf_details = results.get("performance_details", {})
                scores = [
                    perf_details.get("non_fulfillment_normalized", 5),
                    perf_details.get("compliance_normalized", 5),
                    perf_details.get("administrative_normalized", 5)
                ]
            elif selected_risk_category == "Federal Contract":
                risk_factors = ["Agency Diversity", "Competition", "Sub-Agency", "Contract Size", "Contract Type"]
                contract_details = results.get("contract_details", {})
                scores = [
                    contract_details.get("agency_diversity_normalized", 5),
                    contract_details.get("competition_normalized", 5),
                    contract_details.get("sub_agency_normalized", 5),
                    contract_details.get("contract_size_normalized", 5),
                    contract_details.get("contract_type_normalized", 5)
                ]
            elif selected_risk_category == "Foreign Labor":
                risk_factors = ["H1B Dependency", "Country Risk", "Job Sensitivity", "Salary", "Visa Denial"]
                labor_details = results.get("labor_details", {})
                scores = [
                    labor_details.get("h1b_dependency_normalized", 5),
                    labor_details.get("country_risk_normalized", 5),
                    labor_details.get("job_sensitivity_normalized", 5),
                    labor_details.get("salary_normalized", 5),
                    labor_details.get("visa_denial_normalized", 5)
                ]
            else:  # Sanctions Risk
                risk_factors = ["Sanctions Count"]
                sanctions_details = results.get("sanctions_details", {})
                scores = [sanctions_details.get("count_normalized", 0)]

            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=[scores],
                x=risk_factors,
                y=['Risk Level'],
                colorscale=[
                    [0, 'darkgreen'],
                    [0.2, 'green'],
                    [0.4, 'yellow'],
                    [0.6, 'orange'],
                    [0.8, 'red'],
                    [1.0, 'darkred']
                ],
                showscale=True,
                zmin=0,
                zmax=10
            ))

            fig.update_layout(
                title=f"{selected_risk_category} Risk Factors",
                height=250,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

            # Allow downloading results as CSV
            st.download_button(
                label="Download Results as CSV",
                data=pd.DataFrame({
                    'Metric': ['VRRS Score', 'Risk Category'] + list(results['weights_used'].keys()),
                    'Value': [results['vrrs_score'], results['risk_category']] + list(results['weights_used'].values())
                }).to_csv(index=False),
                file_name=f"{company_name}_risk_assessment.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()