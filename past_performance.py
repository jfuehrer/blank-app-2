"""
Past performance scoring module for the Vendor Risk Reliability Score (VRRS) application.
Calculates risk scores based on past contract cancellations and performance issues.
"""

# Cancellation criteria thresholds
CANCELLATION_CRITERIA = {
    "Non-Fulfillment": [1, 5, 10],
    "Compliance": [1, 7, 10],
    "Adminstrative": [5, 8, 10]
}

def get_cancellation_score(cancellation_type, count):
    """
    Determine the cancellation score based on type and count.
    
    Args:
        cancellation_type (str): Type of cancellation ("Non-Fulfillment", "Compliance", "Adminstrative")
        count (int): Number of cancellations of this type
        
    Returns:
        int: Score based on the cancellation type and count
    """
    thresholds = CANCELLATION_CRITERIA.get(cancellation_type, [10, 5, 1])
    if count == 0:
        return thresholds[0]
    elif count == 1:
        return thresholds[1]
    else:
        return thresholds[2]
    
def get_past_performance_cancellation_score(vendor_data):
    """
    Calculate past performance score based on cancellation data.
    
    Args:
        vendor_data (dict): Vendor data containing cancellation information
        
    Returns:
        float: Weighted past performance score
    """
    # Extract cancellation counts, default to 0 if not present
    non_fulfillment_count = vendor_data.get('Non-Fulfillment', 0)
    compliance_count = vendor_data.get('Compliance', 0)
    administrative_count = vendor_data.get('Administrative', 0)  # Fixed spelling
    if administrative_count < 0:
        administrative_count = 0
    
    # Calculate scores for each cancellation type
    non_fulfillment_score = get_cancellation_score("Non-Fulfillment", non_fulfillment_count)
    compliance_score = get_cancellation_score("Compliance", compliance_count)
    adminstrative_score = get_cancellation_score("Adminstrative", administrative_count)

    # Apply weighted formula for final risk score
    weighted_score = (
        (non_fulfillment_score * 0.50) + 
        (compliance_score * 0.35) + 
        (adminstrative_score * 0.15)
    )
    
    return round(weighted_score, 2)

def interpret_past_performance_cancellation_score(score):
    """
    Interpret the past performance cancellation score.
    
    Args:
        score (float): The past performance cancellation score
        
    Returns:
        tuple: (risk_category, interpretation_message)
    """
    # Aligned with VRRS thresholds for consistency
    if score >= 8.0:
        return "Severe Risk", "Vendor has had extensive contract cancellations due to serious non-fulfillment and compliance issues."
    elif 6.5 <= score < 8.0:
        return "High Risk", "Vendor has had significant contract cancellations due to non-fulfillment and compliance issues."
    elif 4.5 <= score < 6.5:
        return "Moderate Risk", "Vendor has had several contracts cancelled in the past."
    elif 2.5 <= score < 4.5:
        return "Low Risk", "Vendor has had few minor contract issues or administrative cancellations."
    else:
        return "Very Low Risk", "Vendor has had no contract cancellations due to non-fulfillment or compliance issues."