# past performance cancellation scoring

CANCELLATION_CRITERIA = {
    "Non-Fulfillment": [10, 5, 1],
    "Compliance": [10, 7, 1],
    "Adminstrative": [10, 8, 5]
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
    
def get_past_performance_score(vendor_data):
    """Calculate past performance score based on cancellation data.
    """
    non_fulfillment_score = get_cancellation_score("Non-Fulfillment", vendor_data['Non-Fulfillment'])
    compliance_score = get_cancellation_score("Compliance", vendor_data['Compliance'])
    adminstrative_score = get_cancellation_score("Adminstrative", vendor_data['Adminstrative'])

    # Apply weighted formula for final risk score
    return (non_fulfillment_score * 0.50) + (compliance_score * 0.35) + (adminstrative_score * 0.15)