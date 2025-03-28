# Josh note: financial stability score is working and has been tested. Need to add interpretation results

# financial stability scoring
FINANCIAL_METRIC_WEIGHTS = {
    'Altman_Z': 0.30,
    'DTE': 0.20,
    'DTI': 0.20,
    'ROA': 0.15,
    'ROE': 0.15
}

METRIC_RANGES = {
    'Altman_Z': [
        (1.0, 1.81, 10), 
        (1.81, 2.99, 5), 
        (2.99, float('inf'), 1)
    ],
    'DTE': [
        (0.0, 0.5, 1), 
        (0.51, 1.0, 3), 
        (1.01, 2.00, 5), 
        (2.01, 3.0, 7), 
        (3, float('inf'), 10)
    ],
    'DTI': [
        (0.0, 0.5, 1), 
        (0.51, 1.0, 3), 
        (1.01, 2.00, 5), 
        (2.01, 3.0, 7), 
        (3, float('inf'), 10)
    ],
    'ROA': [
        (-1.0, -0.50, 10), 
        (-0.49, -0.01, 8),
        (0.0, 0.50, 5),
        (0.51, 0.99, 3),
        (1.0, float('inf'), 1)
    ],
    'ROE': [
        (-1.0, -0.50, 10), 
        (-0.49, -0.01, 8),
        (0.0, 0.50, 5),
        (0.51, 0.99, 3),
        (1.0, float('inf'), 1)
    ]
}

# 1. Generic scoring function based on predefined thresholds
def score_with_thresholds(value, thresholds):
    """Assigns a score based on predefined thresholds."""
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0  # Default score if no match is found


# 2. Function to calculate score for each financial metric
def calculate_financial_metric_score(metric, value):
    """Calculate the financial metric score based on predefined thresholds."""
    return score_with_thresholds(value, METRIC_RANGES.get(metric, []))


# 3. Function to calculate financial stability score
def get_financial_stability_score(vendor_data):
    """Calculate and return the final financial stability score."""
    
    # Ensure vendor_data contains valid numerical values
    financial_metrics = {metric: float(vendor_data.get(metric, 0)) for metric in FINANCIAL_METRIC_WEIGHTS}

    # Calculate scores for each metric
    metric_scores = {
        metric: calculate_financial_metric_score(metric, value) for metric, value in financial_metrics.items()
    }

    # Apply weightings and compute the final score
    weighted_score = sum(metric_scores[metric] * FINANCIAL_METRIC_WEIGHTS[metric] for metric in metric_scores)

    # Normalize by sum of weights (ensuring the score is within the correct range)
    final_score = weighted_score / sum(FINANCIAL_METRIC_WEIGHTS.values())

    return round(final_score, 2)

# basic nterpretation function of results. Can be improved by mapping back to the specific fin elements (e.g., company has strong assets; company has weaker than expected ROI)

def interpret_financial_stability_risk_score(score):
    if score >= 6.1:
        return "Severe Risk", "Potential bankruptcy or major financial distress. Avoid vendor."
    elif 4.0 <= score < 6.0:
        return "High Risk", "Poor financial health; high risk vendor. Consider alternative vendors. If selected, it will require closer monitoring."
    elif 2.0 <= score < 5.9:
        return "Moderate Risk", "Stable financial health."
    else:
        return "Low Risk", "Strong financial health, reliable vendor. Proceed with confidence."