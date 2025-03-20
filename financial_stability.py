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
        (-0.50, -1.0, 10), 
        (-0.01, -0.49, 8),
        (0.50, 0.0, 5),
        (0.2, 0.49, 3),
        (0.5, float('inf'), 1)
    ],
    'ROE': [
        (-0.50, -1.0, 10), 
        (-0.01, -0.49, 8),
        (0.50, 0.0, 5),
        (0.2, 0.49, 3),
        (0.5, float('inf'), 1)
    ]
}


# 01. generic scoring function based on thresholds
def score_with_thresholds(value, thresholds):
    """Score a values based on predefined thresholds"""
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0

# 2. Get Fin Score
def get_vendor_data(METRIC_RANGES, count):
   """Calculate the score for a specific visa category based on counts"""
   return score_with_thresholds(count, METRIC_RANGES.get(count, []))



def get_financial_stability_score(vendor_data):
    """Calculate financial score.
    """
    financial_score = {
        'Altman_Z': vendor_data.get('Altman_Z', 0),
        'DTE': vendor_data.get('DTE', 0),
        'DTI': vendor_data.get('DTI', 0),
        'ROA': vendor_data.get('ROA', 0),
        'ROE': vendor_data.get('ROE', 0)
    }

    final_score = get_financial_stability_score(financial_score)
    return round (financial_score, 2)
    #return ('Altman_Z' * 0.30) + ('DTE' * 0.20) + ('DTI' * 0.20) + ('ROA' * .15) + ('ROE' * .15)
    




'''
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

# josh, these may need to be tweaked in regards to min/max
#METRIC_RANGES = {
#    'Altman_Z': {'min': 1.0, 'max': 10.0, 'reverse': False}, # high is good
#    'DTE': {'min': 0.0, 'max': 5.0, 'reverse': True}, # low is good
#    'DTI': {'min': 0.0, 'max': 3.0, 'reverse': True}, # low is good
#    'ROA': {'min': -1.0, 'max': 0.20, 'reverse': False}, # high is good
#    'ROE': {'min': -1.0, 'max': 0.30, 'reverse': False}, # high is good
#}
'''
# need to define interpretation function