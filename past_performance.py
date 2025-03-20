# past performance cancellation scoring
# updated to reverse scoring to meet Blue/Cabby ask
# added interp function - need to include in overal scoring calculator

CANCELLATION_CRITERIA = {
    "Non-Fulfillment": [1, 5, 10],
    "Compliance": [1, 7, 10],
    "Adminstrative": [5, 8, 10]
}

def get_cancellation_score(cancellation_type, count):
    """Determine the cancellation score based on type and count"""
    thresholds = CANCELLATION_CRITERIA.get(cancellation_type, [10, 5, 1])
    if count == 0:
        return thresholds[0]
    elif count == 1:
        return thresholds[1]
    else:
        return thresholds[2]
    
def get_past_performance_cancellation_score(vendor_data):
    """Calculate past performance score based on cancellation data.
    """
    non_fulfillment_score = get_cancellation_score("Non-Fulfillment", vendor_data['Non-Fulfillment'])
    compliance_score = get_cancellation_score("Compliance", vendor_data['Compliance'])
    adminstrative_score = get_cancellation_score("Adminstrative", vendor_data['Adminstrative'])

    # Apply weighted formula for final risk score
    return (non_fulfillment_score * 0.50) + (compliance_score * 0.35) + (adminstrative_score * 0.15)

#interpretation of past performance cancellation score
def interpret_past_performance_cancellation_score(score):
    if score >= 5.0:
        return "High Risk", "Vendors has had contract cancellations due to non-fulfillment and compliance issues."
    elif 3.0 <= score < 4.9:
        return "Moderate Risk", "Vendor has had some contracts cancelled in the past."
    else:
        return "Low Risk", "Vendor has had no contract cancellations due to non-fulfillment or compliance issues."