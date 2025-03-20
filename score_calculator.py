# this handles orchestration by invoking each scoring function and combing their results
# cabby/blue: can we flip the scoring so it is a higher score (high score = high risk)
# update 1.1

from financial_stability import get_financial_stability_score, interpret_financial_stability_risk_score
from past_performance import get_past_performance_cancellation_score, interpret_past_performance_cancellation_score
from federal_contract import calculate_final_contract_score, interpret_federal_contract_score
from foreign_labor import calculate_final_foreign_labor_score, interpret_foreign_labor_risk_score

# Define weightings for the risk components (adjust as needed)
RISK_WEIGHTS = {
    'financial_stability': 0.35,   # Higher risk for financially unstable vendors
    'contract_performance': 0.30,  # Poor contract performance adds risk
    'foreign_labor_risk': 0.20,    # Dependency on foreign labor increases risk
    'past_performance': 0.15       # Cancellation history affects risk
}

def calculate_vendor_risk_reliability(financial, past, contract, labor):
    """Formula to calculate the final vendor risk reliability score"""
    return round((financial * 0.3) + (past * 0.3) + (contract * 0.2) + (labor * 0.2), 2)

# VRRS risk thresholds and interpretations
VRRS_RISK_THRESHOLDS = [
    (8.5, float('inf'), "Severe Risk", "Vendor is highly unreliable, with financial distress, contract cancellations, compliance violations, or high foreign labor dependency risks for critical roles. Not recommended for contracts."),
    (7.0, 8.49, "High Risk", "Vendor shows significant financial weaknesses, federal contract issues, or foreign labor dependency risks for critical roles. Use only with mitigation strategies."),
    (5.0, 6.99, "Moderate Risk", "Vendor shows some financial instability or contract fulfillment issues and low foreign labor dependency. Due diligence is required before awarding contracts."),
    (3.0, 4.99, "Low Risk", "Vendor is mostly stable with minor past performance or financial concerns and none to low foreign labor dependency. Recommend for partnerships."),
    (1.0, 2.99, "Very Low Risk", "Vendor is financially stable, has strong past performance, diverse federal contracts, and none to low foreign labor dependency. Recommend for partnership.")
]

def determine_risk_category(score, thresholds=VRRS_RISK_THRESHOLDS):
    """Determine the risk category and interpretation based on the score"""
    for lower, upper, category, message in thresholds:
        if lower <= score <= upper:
            return category, message
    return "Unknown Risk", "No interpretation available."

def calculate_scores(vendor_data):
    """
    Calculate all vendor scores and return a comprehensive result dictionary,
    including individual risk interpretations and an overall VRRS interpretation.
    """

    # Calculate individual risk scores
    financial_stability_score = get_financial_stability_score(vendor_data)
    past_performance_cancellation_score = get_past_performance_cancellation_score(vendor_data)
    federal_contract_score = calculate_final_contract_score(vendor_data)
    foreign_labor_score = calculate_final_foreign_labor_score(vendor_data)

    # Calculate final VRRS score
    vrrs_score = calculate_vendor_risk_reliability(
        financial_stability_score,
        past_performance_cancellation_score,
        federal_contract_score,
        foreign_labor_score
    )

    # Interpret individual scores
    fin_risk_category, fin_interpretation = interpret_financial_stability_risk_score(financial_stability_score)
    past_risk_category, past_interpretation = interpret_past_performance_cancellation_score(past_performance_cancellation_score)
    contract_risk_category, contract_interpretation = interpret_federal_contract_score(federal_contract_score)
    labor_risk_category, labor_interpretation = interpret_foreign_labor_risk_score(foreign_labor_score)

    # Interpret the VRRS score
    vrrs_risk_category, vrrs_interpretation = determine_risk_category(vrrs_score)

    # Combine individual interpretations into the final interpretation
    combined_interpretation = (
        f"**Overall Risk Assessment:** {vrrs_interpretation}\n\n"
        f"**Financial Stability:** {fin_interpretation}\n"
        f"**Past Performance:** {past_interpretation}\n"
        f"**Federal Contracts:** {contract_interpretation}\n"
        f"**Foreign Labor Risk:** {labor_interpretation}"
    )

    return {
        "financial_stability_score": financial_stability_score,
        "past_performance_cancellation_score": past_performance_cancellation_score,
        "federal_contract_score": federal_contract_score,
        "foreign_labor_score": foreign_labor_score,
        "vrrs_score": vrrs_score,
        "risk_category": vrrs_risk_category,
        "interpretation": combined_interpretation
    }

