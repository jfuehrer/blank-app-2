# financial stability scoring
FINANCIAL_METRIC_WEIGHTS = {
    'Altman_Z': 0.30,
    'DTE': 0.20,
    'DTI': 0.20,
    'ROA': 0.15,
    'ROE': 0.15
}

# josh, these may need to be tweaked in regards to min/max
METRIC_RANGES = {
    'Altman_Z': {'min': 1.0, 'max': 10.0, 'reverse': False}, # high is good
    'DTE': {'min': 0.0, 'max': 5.0, 'reverse': True}, # low is good
    'DTI': {'min': 0.0, 'max': 3.0, 'reverse': True}, # low is good
    'ROA': {'min': -1.0, 'max': 0.20, 'reverse': False}, # high is good
    'ROE': {'min': -1.0, 'max': 0.30, 'reverse': False}, # high is good
}

def normalize_metric(value, min_val, max_val, reverse=False):
    #apply a basic normalization
    value = max(min(value, max_val), min_val)
    normalized = (value - min_val) / (max_val - min_val)
    score = normalized * 9 + 1
    return 10 - score if reverse else score

def get_financial_stability_score(row, weights=FINANCIAL_METRIC_WEIGHTS):
    """
    Calculate financial stability scoring using weighted financial metrics
    """
    normalized_scores = [
        normalize_metric(
            row[col], 
            METRIC_RANGES[col]['min'], 
            METRIC_RANGES[col]['max'],
            METRIC_RANGES[col]['reverse']
        )
        for col in weights.keys()
    ]
    # apply weights to normalized scores
    weighted_score = sum(score * weights[col] for score, col in zip(normalized_scores, weights.keys()))

    # normalize final score
    return round(weighted_score / sum(weights.values()), 2)


# need to define interpretation function