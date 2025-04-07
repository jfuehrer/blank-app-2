"""
Vendor Risk Reliability Score (VRRS) calculator
This module handles orchestration by invoking each scoring function and combining their results

Note on scoring consistency:
- Financial stability, past performance, federal contract, and foreign labor scores use a 0-10 scale
- Sanctions risk score is received on a 0-100 scale but is normalized to 0-10 for consistent VRRS calculation
"""

from financial_stability import get_financial_stability_score, interpret_financial_stability_risk_score
from past_performance import get_past_performance_cancellation_score, interpret_past_performance_cancellation_score
from federal_contract import calculate_final_contract_score, interpret_federal_contract_score
from foreign_labor import calculate_final_foreign_labor_score_with_trend, interpret_foreign_labor_risk_score
from sanctions import get_sanctions_score, interpret_sanctions_score


# Default weightings for the risk components
DEFAULT_RISK_WEIGHTS = {
    'financial_stability': 0.30,   # Higher risk for financially unstable vendors
    'past_performance': 0.25,      # Cancellation history affects risk  
    'federal_contract': 0.15,      # Contract diversity
    'foreign_labor_risk': 0.20,    # Dependency on foreign labor increases risk
    'sanctions_risk': 0.10         # Sanctions risk from global sanctions lists
}

def calculate_vendor_risk_reliability(financial, past, contract, labor, sanctions, weights=None):
    """
    Formula to calculate the final vendor risk reliability score

    Args:
        financial (float): Financial stability score
        past (float): Past performance score
        contract (float): Federal contract score
        labor (float): Foreign labor risk score
        sanctions (float): Sanctions risk score
        weights (dict): Custom weights for each component

    Returns:
        float: Weighted risk reliability score
    """
    if weights is None:
        weights = DEFAULT_RISK_WEIGHTS

    # Normalize weights to ensure they sum to 1.0
    total_weight = sum(weights.values())
    normalized_weights = {k: v/total_weight for k, v in weights.items()}

    # Calculate each component's contribution to the score
    financial_contribution = financial * normalized_weights['financial_stability']
    past_contribution = past * normalized_weights['past_performance']
    contract_contribution = contract * normalized_weights['federal_contract']
    labor_contribution = labor * normalized_weights['foreign_labor_risk']
    sanctions_contribution = sanctions * normalized_weights['sanctions_risk']
    
    # Sum all contributions
    weighted_score = (
        financial_contribution +
        past_contribution +
        contract_contribution +
        labor_contribution +
        sanctions_contribution
    )
    
    # Print for debugging
    print(f"\nVRRS Score Calculation:")
    print(f"Financial: {financial:.2f} × {normalized_weights['financial_stability']:.2f} = {financial_contribution:.2f}")
    print(f"Past Performance: {past:.2f} × {normalized_weights['past_performance']:.2f} = {past_contribution:.2f}")
    print(f"Federal Contract: {contract:.2f} × {normalized_weights['federal_contract']:.2f} = {contract_contribution:.2f}")
    print(f"Foreign Labor: {labor:.2f} × {normalized_weights['foreign_labor_risk']:.2f} = {labor_contribution:.2f}")
    print(f"Sanctions: {sanctions:.2f} × {normalized_weights['sanctions_risk']:.2f} = {sanctions_contribution:.2f}")
    print(f"Total VRRS Score: {weighted_score:.2f}\n")

    # Return with 2 decimal places, but don't round the value itself
    # which could cause inconsistencies with the true weighted score
    return float(f"{weighted_score:.2f}")

# VRRS risk thresholds and interpretations
VRRS_RISK_THRESHOLDS = [
    (8.0, float('inf'), "Severe Risk", "Vendor is highly unreliable, with financial distress, contract cancellations, compliance violations, legal issues, sanctions, or high foreign labor dependency risks. Not recommended for contracts."),
    (6.5, 7.99, "High Risk", "Vendor shows significant financial weaknesses, legal/sanctions issues, federal contract issues, or foreign labor dependency risks. Use only with mitigation strategies."),
    (4.5, 6.49, "Moderate Risk", "Vendor shows some financial instability, potential legal concerns, or contract fulfillment issues and low foreign labor dependency. Due diligence is required before awarding contracts."),
    (2.5, 4.49, "Low Risk", "Vendor is mostly stable with minor past performance, legal, or financial concerns and none to low foreign labor dependency. Recommend for partnerships."),
    (0, 2.49, "Very Low Risk", "Vendor is financially stable, has strong past performance, no significant legal/sanctions issues, diverse federal contracts, and none to low foreign labor dependency. Recommend for partnership.")
]


def determine_risk_category(score, thresholds=VRRS_RISK_THRESHOLDS):
    """
    Determine the risk category and interpretation based on the score

    Args:
        score (float): VRRS score
        thresholds (list): Risk threshold definitions

    Returns:
        tuple: (category, message) risk category and interpretation
    """
    for lower, upper, category, message in thresholds:
        if lower <= score <= upper:
            return category, message
    return "Unknown Risk", "No interpretation available."


def calculate_scores(vendor_data, custom_weights=None):
    """
    Calculate all vendor scores and return a comprehensive result dictionary,
    including individual risk interpretations and an overall VRRS interpretation.

    Args:
        vendor_data (dict): Vendor data dictionary with all required fields
        custom_weights (dict, optional): Custom weights for risk components

    Returns:
        dict: Comprehensive risk assessment results
    """
    # Use default weights if no custom weights provided
    weights = custom_weights if custom_weights else DEFAULT_RISK_WEIGHTS

    # Calculate individual risk scores
    financial_stability_score = get_financial_stability_score(vendor_data)
    past_performance_cancellation_score = get_past_performance_cancellation_score(vendor_data)
    federal_contract_score = calculate_final_contract_score(vendor_data)
    sanctions_risk_score = get_sanctions_score(vendor_data)
    
    # Get foreign labor score which returns a dictionary with detailed results
    foreign_labor_result = calculate_final_foreign_labor_score_with_trend(vendor_data)
    
    # Extract just the score from the result
    if isinstance(foreign_labor_result, dict):
        foreign_labor_score = foreign_labor_result.get('foreign_labor_score', 5.0)
        # Store the detailed results for later use
        vendor_data['foreign_labor_trend'] = foreign_labor_result
    else:
        # Fallback if the result is already a number
        foreign_labor_score = foreign_labor_result

    # Get legal and sanctions risk scores from vendor data
    # Note: Previously we expected 0-100 scale but now utils.py gives us scores in 0-10 range
    sanctions_risk_score_raw = vendor_data.get('sanctions_risk_score', 0)

    if sanctions_risk_score_raw <= 10:
        sanctions_risk_score = sanctions_risk_score_raw  # Already on 0-10 scale
        # For interpretation thresholds, we still need the 0-100 value
        sanctions_risk_score_for_interp = sanctions_risk_score_raw * 10
    else:
        # Old format - normalize from 0-100 to 0-10
        sanctions_risk_score = sanctions_risk_score_raw / 10 if sanctions_risk_score_raw <= 100 else 10
        sanctions_risk_score_for_interp = sanctions_risk_score_raw

    # Calculate final VRRS score including sanctions risk but excluding legal risk
    vrrs_score = calculate_vendor_risk_reliability(
        financial_stability_score,
        past_performance_cancellation_score,
        federal_contract_score,
        foreign_labor_score,
        sanctions_risk_score,
        weights
    )

    # Interpret individual scores
    fin_risk_category, fin_interpretation = interpret_financial_stability_risk_score(financial_stability_score)
    past_risk_category, past_interpretation = interpret_past_performance_cancellation_score(past_performance_cancellation_score)
    contract_risk_category, contract_interpretation = interpret_federal_contract_score(federal_contract_score)
    labor_risk_category, labor_interpretation = interpret_foreign_labor_risk_score(foreign_labor_score)

    # For legal and sanctions, we need to use the 0-100 scale scores for interpretation
    # but save the normalized 0-10 scores for VRRS calculation
    sanctions_risk_category, sanctions_interpretation = interpret_sanctions_score(sanctions_risk_score_for_interp)

    # Interpret the VRRS score
    vrrs_risk_category, vrrs_interpretation = determine_risk_category(vrrs_score)

    # Combine individual interpretations into the final interpretation (legal risk removed)
    combined_interpretation = (
        f"**Overall Risk Assessment:** {vrrs_interpretation}\n\n"
        f"**Financial Stability:** {fin_interpretation}\n"
        f"**Past Performance:** {past_interpretation}\n"
        f"**Federal Contracts:** {contract_interpretation}\n"
        f"**Foreign Labor Risk:** {labor_interpretation}\n"
        f"**Sanctions Risk:** {sanctions_interpretation}"
    )

    # Extract detailed financial metrics for heat map - use the metrics from vendor_data directly
    # Financial details can be found directly in the vendor_data structure
    if 'financial' in vendor_data and isinstance(vendor_data['financial'], dict):
        # Use the pre-calculated normalized values from the demo data
        financial_details = vendor_data['financial']
    else:
        # Fallback to default values
        financial_details = {
            "altman_z_score_normalized": 5.0,
            "debt_to_equity_normalized": 5.0,
            "debt_to_income_normalized": 5.0,
            "return_on_assets_normalized": 5.0,
            "return_on_equity_normalized": 5.0
        }

    # Extract detailed past performance metrics for heat map
    if 'past_performance' in vendor_data and isinstance(vendor_data['past_performance'], dict):
        # Use the pre-calculated normalized values from the demo data
        performance_details = vendor_data['past_performance']
    else:
        # Fallback to default values
        performance_details = {
            "non_fulfillment_normalized": 5.0,
            "compliance_normalized": 5.0,
            "administrative_normalized": 5.0
        }

    # Extract detailed federal contract metrics for heat map
    if 'federal_contract' in vendor_data and isinstance(vendor_data['federal_contract'], dict):
        # Use the pre-calculated normalized values from the demo data
        contract_details = vendor_data['federal_contract']
    else:
        # Fallback to default values
        contract_details = {
            "agency_diversity_normalized": 5.0,
            "competition_normalized": 5.0,
            "sub_agency_normalized": 5.0,
            "contract_size_normalized": 5.0,
            "contract_type_normalized": 5.0
        }

    # Extract detailed foreign labor metrics for heat map
    if 'foreign_labor' in vendor_data and isinstance(vendor_data['foreign_labor'], dict):
        # Use the pre-calculated normalized values from the demo data
        labor_details = vendor_data['foreign_labor']
    else:
        # Fallback to default values
        labor_details = {
            "h1b_dependency_normalized": 5.0,
            "country_risk_normalized": 5.0,
            "job_sensitivity_normalized": 5.0,
            "salary_normalized": 5.0,
            "visa_denial_normalized": 5.0
        }

    # Extract detailed legal metrics for heat map
    # Extract sanctions metrics for heat map (only count rows with text in Sanctions column)
    # Get the sanctions risk score already calculated in utils.py (now on 0-10 scale)
    # This score is based on counting rows with text in the Sanctions column

    # Use the already calculated sanctions_risk_score directly
    count_score = sanctions_risk_score

    # Simplified sanctions details for heat map - using only a single metric now
    sanctions_details = {
        "count_normalized": count_score  # The only metric we care about now
    }

    return {
        "vendor_name": vendor_data.get('Vendor', 'Unknown Vendor'),
        "financial_stability_score": financial_stability_score,
        "financial_stability_category": fin_risk_category,
        "financial_details": financial_details,
        
        # Include trend analysis if available
        "trend_analysis": vendor_data.get('trend_analysis', {}),
        "financial_point_in_time_score": vendor_data.get('financial_point_in_time_score', 0.0),
        "financial_trend_score": vendor_data.get('financial_trend_score', 0.0),

        "past_performance_score": past_performance_cancellation_score,
        "past_performance_category": past_risk_category,
        "performance_details": performance_details,

        "federal_contract_score": federal_contract_score,
        "federal_contract_category": contract_risk_category,
        "contract_details": contract_details,

        "foreign_labor_score": foreign_labor_score,
        "foreign_labor_category": labor_risk_category,
        "labor_details": labor_details,
        "foreign_labor_trend": vendor_data.get('foreign_labor_trend', None),
        "visa_trend_analysis": vendor_data.get('visa_trend_analysis', {}),

        "sanctions_score": sanctions_risk_score,
        "sanctions_category": sanctions_risk_category,
        "sanctions_details": sanctions_details,

        "vrrs_score": vrrs_score,
        "risk_category": vrrs_risk_category,
        "interpretation": combined_interpretation,
        "weights_used": weights
    }