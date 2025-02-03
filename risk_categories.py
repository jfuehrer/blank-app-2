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