# this handles orchestration by invoking each scoring function and combing their results
# cabby/blue: can we flip the scoring so it is a higher score (high score = high risk)
# update 1.1

# import functions from other modules
from financial_stability import get_financial_stability_score
from past_performance import get_past_performance_cancellation_score
from federal_contract import calculate_final_contract_score
from foreign_labor import calculate_final_foreign_labor_score


# Define weightings for the risk components (adjust as needed)
RISK_WEIGHTS = {
    'financial_stability': 0.35,   # Higher risk for financially unstable vendors
    'contract_performance': 0.30,  # Poor contract performance adds risk
    'foreign_labor_risk': 0.20,    # Dependency on foreign labor increases risk
    'past_performance': 0.15       # Cancellation history affects risk
}


def calculate_vendor_risk_reliability(financial, past, contract, labor):
    """Example formulate for calculating the final vendor risk relaiblity score"""
    return round((financial * 0.3) + (past * 0.3) + (contract * 0.2) +(labor * 0.2), 2)

# contains the risk category thresholds and interpretations for VRRS and other scores
VRRS_RISK_THRESHOLDS = [
    (8.5, float('inf'), "Severe Risk", "Vendor is highly unreliable, with financial distress, contract cancellations, compliance violations, or high foreign labor dependency risks for critical roles. Not recommended for contracts."),
    (7.0, 8.49, "High Risk", "Vendor shows significant financial weaknesses, federal contract issues, or foreign labor dependency risks for critical roles. Use only with mitigation strategies."),
    (5.0, 6.99, "Moderate Risk", "Vendor shows some financial instability or contract fulfillment issues and low foreign labor dependency. Due diligence is required before awarding contracts."),
    (3.0, 4.99, "Low Risk", "Vendor is mostly stable with minor past performance or financial concerns and none to low foreign labor dependency. Recommend for partnerships."),
    (1.0, 2.99, "Very Low Risk", "Vendor is financially stable, has strong past performance, diverse federal contracts, and none to low foreign labor dependency. Recommend for partnership.")
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
    #Calculate all vendor scores and return a comp result dictionary
    #return: Final risk score (higher = more risk).

    financial_stability_score = get_financial_stability_score(vendor_data)
    past_performance_cancellation_score = get_past_performance_cancellation_score(vendor_data)
    federal_contract_score = calculate_final_contract_score(vendor_data)
    foreign_labor_score = calculate_final_foreign_labor_score(vendor_data)
    # Reverse scores where higher = more risk


    #calculate final VRRS score
    vrrs_score = calculate_vendor_risk_reliability(
        financial_stability_score,
        past_performance_cancellation_score,
        federal_contract_score,
        foreign_labor_score
    )

    # interpret the VRRS score
    risk_category, interpretation = determine_risk_category(vrrs_score)

    return {
        "financial_stability_score": financial_stability_score,
        "past_performance_cancellation_score": past_performance_cancellation_score,
        "federal_contract_score": federal_contract_score,
        "foreign_labor_score": foreign_labor_score,
        "vrrs_score": vrrs_score,
        "risk_category": risk_category,
        "interpretation": interpretation
    }

'''
'# insert old
VRRS_RISK_THRESHOLDS = [
    (8.5, float('inf'), "Very Low Risk", "Vendor is financially stable, has strong past performance, diverse federal contracts, and none to low foreign labor dependency. Recommend for partnership."),
    (7.0, 8.49, "Low Risk", "Vendor is mostly stable with minor past performance or financial concerns and none to low foreign labor dependency. Recommend for partnerships."),
    (5.0, 6.99, "Moderate Risk", "Vendor shows some financial instability or contract fulfillment issues and low foreign labor dependency. Due diligence is required before awarding contracts."),
    (3.0, 4.99, "High Risk", "Vendor shows significant financial weaknesses, federal contract issues, or foreign labor dependency risks for critical roles. Use only with mitigation strategies."),
    (1.0 - 2.00, "Severe Risk", "Vendor is highly unreliable, with financial distress, contract cancellations, compliance violations, or high foreign labor dependency risks for critical roles. Not recommended for contracts.")
]

# insert old
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

def normalize_and_reverse_score(score, scale_min=0, scale_max=10):
    """
    Normalize and reverse a score to fit within the 0-10 risk scale where 10 = highest risk.
    :param score: Original score to normalize and reverse.
    :param scale_min: Minimum possible score.
    :param scale_max: Maximum possible score.
    :return: Normalized and reversed risk score.
    """
    normalized = (score - scale_min) / (scale_max - scale_min) * 10
    return round(10 - normalized, 2)  # Invert so higher scores mean more risk

def calculate_scores(vendor_data):
    """
    Calculate the Vendor Risk Reliability Score (VRRS) based on multiple risk factors.
    :param vendor_data: Dictionary containing vendor scoring data.
    :return: Final risk score (higher = more risk).
    """
    # Get scores from individual modules
    financial_stability_score = get_financial_stability_score(vendor_data)
    contract_performance_score = calculate_final_contract_score(vendor_data)
    foreign_labor_risk_score = calculate_final_foreign_labor_score(vendor_data)
    past_performance_cancellation_score = get_past_performance_cancellation_score(vendor_data)

    # Reverse scores where higher = more risk
    reversed_scores = {
        'financial_stability': financial_stability_score, # Already scaled correctly
        'contract_performance': normalize_and_reverse_score(contract_performance_score),
        'foreign_labor_risk': foreign_labor_risk_score,  # Already scaled correctly
        'past_performance': get_past_performance_cancellation_score  # Already scaled correctly
    }

    # Calculate the weighted final risk score
    final_risk_score = sum(
        reversed_scores[key] * RISK_WEIGHTS[key] for key in RISK_WEIGHTS.keys()
    )

    # interpret the VRRS score
    risk_category, interpretation = determine_risk_category(final_risk_score)

    return {
        "financial_stability_score": financial_stability_score,
        "past_performance_score": past_performance_cancellation_score,
        "federal_contract_score": contract_performance_score,
        "foreign_labor_score": foreign_labor_risk_score,
        "vrrs_score": final_risk_score,
         "risk_category": risk_category,
        "interpretation": interpretation
    }

    return round(final_risk_score, 2)

# see above
'''