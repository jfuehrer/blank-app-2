# financial stability scoring
FINANCIAL_METRIC_WEIGHTS = {
    'Altman_Z': 0.30,
    'DTE': 0.20,
    'DTI': 0.20,
    'ROA': 0.15,
    'ROE': 0.15
}

def get_financial_stability_score(vendor_data):
    """
    Calculate financial stability scoring using weighted financial metrics
    """
    weighted_score = sum(
        vendor_data.get(metric, 0) * weight for metric, weight in FINANCIAL_METRIC_WEIGHTS.items()
    )
    return round(weighted_score / sum(FINANCIAL_METRIC_WEIGHTS.values()), 2)