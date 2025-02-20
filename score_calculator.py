# this handles orchestration by invoking each scoring function and combing their results
# cabby/blue: can we flip the scoring so it is a higher score (high score = high risk)

# import functions from other modules
from financial_stability import get_financial_stability_score
from past_performance import get_past_performance_score
from federal_contract import calculate_final_contract_score
from foreign_labor import calculate_final_foreign_labor_score

def calculate_vendor_risk_reliability(financial, past, contract, labor):
    """Example formulate for calculating the final vendor risk relaiblity score"""
    return round((financial * 0.3) + (past * 0.3) + (contract * 0.2) +(labor * 0.2), 2)


# contains the risk category thresholds and interpretations for VRRS and other scores
VRRS_RISK_THRESHOLDS = [
    (8.5, float('inf'), "Very Low Risk", "Vendor is financially stable, has strong past performance, diverse federal contracts, and none to low foreign labor dependency. Recommend for partnership."),
    (7.0, 8.49, "Low Risk", "Vendor is mostly stable with minor past performance or financial concerns and none to low foreign labor dependency. Recommend for partnerships."),
    (5.0, 6.99, "Moderate Risk", "Vendor shows some financial instability or contract fulfillment issues and low foreign labor dependency. Due diligence is required before awarding contracts."),
    (3.0, 4.99, "High Risk", "Vendor shows significant financial weaknesses, federal contract issues, or foreign labor dependency risks for critical roles. Use only with mitigation strategies."),
    (1.0 - 2.00, "Severe Risk", "Vendor is highly unreliable, with financial distress, contract cancellations, compliance violations, or high foreign labor dependency risks for critical roles. Not recommended for contracts.")
]

def determine_risk_category(score, thresholds=VRRS_RISK_THRESHOLDS):
    """Determine the risk category and interpretation based on the score
    :param score: the numeric risk score to evaluate
    :param thresholds: List of thresholds with low, upper, category, message
    :return: A tuple containing (risk_category, interpretation)
    """
    for lower, upper, category, message in thresholds:
        if lower <= score <= upper:
            return category, message
    return "Unknown risk", "No interpretation available"

def calculate_scores(vendor_data):
    """Calculate all vendor scores and return a comphrensive result dictionary"""
    financial_stability_score = get_financial_stability_score(vendor_data)
    past_performance_score = get_past_performance_score(vendor_data)
    federal_contract_score = calculate_final_contract_score(vendor_data)
    foreign_labor_score = calculate_final_foreign_labor_score(vendor_data)

    #calculate final VRRS score
    vrrs_score = calculate_vendor_risk_reliability(
        financial_stability_score,
        past_performance_score,
        federal_contract_score,
        foreign_labor_score
    )

    # interpret the VRRS score
    risk_category, interpretation = determine_risk_category(vrrs_score)

    return {
        "financial_stability_score": financial_stability_score,
        "past_performance_score": past_performance_score,
        "federal_contract_score": federal_contract_score,
        "foreign_labor_score": foreign_labor_score,
        "vrrs_score": vrrs_score,
        "risk_category": risk_category,
        "interpretation": interpretation
    }
