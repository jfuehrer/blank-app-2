import streamlit as st
import pandas as pandas

def calculate_vendor_risk_reliability_score(financial_stability_score, past_cancellation_score, federal_contract_score, foreign_labor_score):
    """
    Calculate VRRS

    Parameters:
        financial_stability_score (float): Financial Stablity Risk Score (1-10).
        past_cancellation_score (float): Past Performance Contract Cancellation Score (1-10).
        federal_contract_score (float): Federal Contract Financial Source Score (1-10).
        foreign_labor_score (float): Foreign Labor Risk Score (1-10).
    
        Returns:
            float: The Vendor Risk Reliability Score
        """
    # define weight factors
    financial_weight = 0.40
    past_cancellation_weight = 0.20
    federal_contract_weight = 0.10
    foreign_labor_weight = 0.30

    #calculate the weighted risk score
    vrrs_score = (
        (financial_stability_score * financial_weight) +
        (past_cancellation_score * past_cancellation_weight) +
        (federal_contract_score * federal_contract_weight) +
        (foreign_labor_score * foreign_labor_weight)
    )

    return vrrs_score

def interpret_vendor_risk_reliability_score(vrrs_score):
    """
    Interpret the VRRS.

    Parameters:
        vrrs_score (float): The VRRS.
    
    Returns:
        dict: A dictionary with risk level, interpretation, and recommendation.
    """
    if 8.5 <= vrrs_score <= 10.0:
        return {
            "Risk Level": "Very Low Risk",
            "Interpretation": "Vendor is financially stable, has strong past performance, diverse federal contracts, and none to low foreign labor dependency. Recommend for partnership."
        }
    elif 7.0 <= vrrs_score < 8.5:
        return {
           "Risk Level": "Low Risk",
           "Interpretation": "Vendor is mostly stable with minor past performance or financial concerns and none to low foreign labor dependency. Recommend for partnerships." 
        }
    elif 5.0 <= vrrs_score < 7.0:
        return {
          "Risk Level": "Moderate Risk",
          "Interpretation": "Vendor shows some financial instability or contract fulfillment issues and low foreign labor dependency. Due diligence is required before awarding contracts." 
        }
    elif 3.0 <= vrrs_score < 5.0:
        return {
          "Risk Level": "High Risk",
          "Interpretation": "Vendor shows significant financial weaknesses, federal contract issues, or foreign labor dependency risks for critical roles. Use only with mitigation strategies."   
        }
    elif 1.0 <= vrrs_score < 3.0:
        return {
            "Risk Level": "Severe Risk",
            "Interpretation": "Vendor is highly unreliable, with financial distress, contract cancellations, compliance violations, or high foreign labor dependency risks for critical roles. Not recommended for contracts. "   
        }
    else:
        return {
            "Risk Level": "Invalid Source",
            "Interpretation": "The VRRS score is out of the valid range (1.0 to 10.).",
        }

# import functions from other modules
from vendor_financial_stability_score import get_financial_stability_score
from vendor_past_performance_contract_cancellation_score import get_cancellation_risk_score
from vendor_federal_contract_financial_source_score import get_performance_score
from vendor_foreign_labor_score import get_foreign_labor_risk_score

def main():
    #retrieve scores
    financial_stability_score = get_financial_stability_score()
    past_cancellation_score = get_cancellation_risk_score()
    federal_contract_score = get_performance_score()
    foreign_labor_score = get_foreign_labor_risk_score()

    #calculate VRRS score
    vrrs_score = calculate_vendor_risk_reliability_score(
        financial_stability_score,
        past_cancellation_score,
        federal_contract_score,
        foreign_labor_score
    )

    # interpret the vrrs score
    result = interpret_vendor_risk_reliability_score(vrrs_score)

    #display the interpretation
    print("Vendor Risk Reliability Score Interpretation:")
    for key, value in result.items():
        print(f"{key}: {value}")