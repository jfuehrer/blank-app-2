# Define updated thresholds to align with military preference (higher score = higher risk)
VRRS_RISK_THRESHOLDS = [
    (8.0, float('inf'), "Severe Risk", "Vendor is unreliable with severe risks. Avoid if possible."),
    (6.0, 7.99, "High Risk", "Vendor has high risk and may require close monitoring."),
    (4.0, 5.99, "Moderate Risk", "Vendor is stable with moderate risk."),
    (0.0, 3.99, "Low Risk", "Vendor is reliable and has minimal risk.")
]

def calculate_risk_score(vendor_data):
    """
    Calculate a vendor's risk score based on multiple weighted factors.
    :param vendor_data: Dictionary containing vendor metrics.
    :return: Final risk score (higher score = higher risk).
    """
    # Define weightings for different risk components
    WEIGHTS = {
        'financial_stability': 0.40,  # Higher stability = lower risk
        'contract_performance': 0.30, # Higher performance = lower risk
        'foreign_labor_risk': 0.20,   # Higher foreign labor dependence = higher risk
        'past_cancellations': 0.10    # More cancellations = higher risk
    }

    # Normalize inputs to a common scale (0-10)
    normalized_scores = {
        'financial_stability': 10 - vendor_data['financial_stability_score'],  # Reverse financial stability
        'contract_performance': 10 - vendor_data['contract_performance_score'],  # Reverse contract performance
        'foreign_labor_risk': vendor_data['foreign_labor_risk_score'],  # No reversal needed
        'past_cancellations': vendor_data['past_cancellations_score']  # No reversal needed
    }

    # Compute weighted risk score
    risk_score = sum(normalized_scores[key] * WEIGHTS[key] for key in WEIGHTS.keys())

    # Ensure risk score remains within 0-10
    return round(min(max(risk_score, 0), 10), 2)

def determine_risk_category(score, thresholds=VRRS_RISK_THRESHOLDS):
    """
    Determine the risk category and interpretation based on the calculated risk score.
    :param score: The numeric risk score to evaluate.
    :return: A tuple containing (risk_category, interpretation).
    """
    for lower, upper, category, message in thresholds:
        if lower <= score <= upper:
            return category, message
    return "Unknown Risk", "No interpretation available."

# Example vendor data
vendor_data_example = {
    'financial_stability_score': 8.5,  # Higher = more stable (low risk)
    'contract_performance_score': 7.2,  # Higher = better performance (low risk)
    'foreign_labor_risk_score': 5.5,  # Higher = greater labor risk
    'past_cancellations_score': 4.0  # Higher = worse cancellation record
}

# Calculate and categorize risk score
final_risk_score = calculate_risk_score(vendor_data_example)
risk_category, interpretation = determine_risk_category(final_risk_score)

# Display results
print(f"Final Risk Score: {final_risk_score}")
print(f"Category: {risk_category}")
print(f"Interpretation: {interpretation}")
