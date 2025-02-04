# foreign labor scoring


FOREIGN_LABOR_PERCENTAGE_THRESHOLDS = [
    (0, 0, 10), #0% foreign labor receives a perfect score
    (1, 10, 8), #1% to 10% foreign labor gets a score of 8
    (11, 20, 6), # 11% to 20% foreign labor gets a score of 6 
    (21, 50, 4), # 21% to 50% foreign labor gets a score of 4
    (51, float('inf'), 2) # Greate than 50% gets a score of 2
]

COUNTRY_RISK_MULTIPLIER = {
    'low_risk': 1.0,
    'moderate_risk': 0.8,
    'high-risk': 0.6
}

RISK_CATEGORIZATION = {
    'low_risk': ['USA', 'Canada', 'Germany', 'France'],
    'moderate_risk': ['India', 'Brazil', 'South Korea'],
    'high_risk': ['Russia', 'China', 'Iran']   
}

VISA_CATEGORY_THRESHOLDS = {
    'certified': [
        (0, 10, 10), 
        (11, 20, 8), 
        (21, 50, 6), 
        (51, float('inf'), 4)
    ],
    'denied': [
        (0, 10, 6), 
        (11, 20, 4), 
        (21, 50, 2), 
        (51, float('inf'), 1)
    ],
    'withdrawn': [
        (0, 10, 6), 
        (11, 20, 4), 
        (21, 50, 2), 
        (51, float('inf'), 1)
    ],
    'certified_expired': [
        (0, 10, 6), 
        (11, 20, 4), 
        (21, 50, 2), 
        (51, float('inf'), 1)
    ],
    'unspecified': [
        (0, 10, 6), 
        (11, 20, 4), 
        (21, 50, 2), 
        (51, float('inf'), 1)
    ]
}

TREND_ADJUSTMENT = {
    'favorable': 10,
    'neutral': 6,
    'unfavorable': 2
}

# generic scoring function based on thresholds
def score_with_thresholds(value, thresholds):
    """Score a values based on predefined thresholds"""
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0

# 1. Foreign Labor Percentage Score
def get_foreign_labor_score(percentage):
    """Calculate the foreign labor score based on labor percentage"""
    return score_with_thresholds(percentage, FOREIGN_LABOR_PERCENTAGE_THRESHOLDS)

# 2. Country risk multipler
def get_country_risk_multiplier(country):
    """Get the risk multipler based on the country."""
    for risk_level, countries in RISK_CATEGORIZATION.items():
        if country in countries:
            return COUNTRY_RISK_MULTIPLIER[risk_level]
    return COUNTRY_RISK_MULTIPLIER['moderate_risk']

# 3. Job Sensitivity Score
def calculate_job_sensitivity_score(low, moderate, high):
    """Calculate the job sensitivity score based on the number of job types"""
    total_jobs = low + moderate + high
    if total_jobs == 0:
        return 10 # no freign labor means minimal job risk
    weighted_score = ((low * 10) + (moderate * 6) + (high * 2)) / total_jobs
    return round(weighted_score, 2)

# 4. Visa Category Score
def get_visa_category_score(category, count):
    """Calculate the score for a specific visa category based on counts"""
    return score_with_thresholds(count, VISA_CATEGORY_THRESHOLDS.get(category, []))

def calculate_visa_data_score(visa_counts):
    """Calculate the overall score based on multiple visa categories"""
    total_count = sum(visa_counts.values())
    if total_count == 0:
        return 10 # no visa data implies min risk
    score_sum = sum(get_visa_category_score(category, count) for category, count in visa_counts.items())
    return round(score_sum / len(visa_counts), 2)

# 5. Visa Trend Adjustment Score
def get_visa_trend_adjustment(trend_data):
    """Adjust the visa score based on recent trends"""
    if trend_data['denied_withdrawn_trend'] == 10 or trend_data['ceritifed_trend'] == 10:
        return TREND_ADJUSTMENT['favorable']
    elif trend_data['certified_trend'] == 6 and trend_data['denied_withdrawn_trend'] == 6:
        return TREND_ADJUSTMENT['neutral']
    else:
        return TREND_ADJUSTMENT['unfavorable']
    
# 6. permanent visa score
def calculate_permanent_visa_score(visa_counts, trend_data):
    """Calculate the score for permanent visa applications"""
    visa_data_score = calculate_visa_data_score(visa_counts)
    trend_adjustment = get_visa_trend_adjustment(trend_data)
    return round((visa_data_score * 0.70) + (trend_adjustment * 0.3), 2)

# 7. Final Foreign Labor Risk Score
def calculate_final_foreign_labor_score(vendor_data):
    """Calculate the final foreign labor score for a vendor"""
    foreign_labor_score = get_foreign_labor_score(vendor_data['foreign_labor_percentage'])
    country_multiplier = get_country_risk_multiplier(vendor_data['country'])

    adjusted_foreign_labor_score = foreign_labor_score * country_multiplier
    job_sensitivity_score = calculate_job_sensitivity_score(
        vendor_data['job_counts_low'], vendor_data['job_counts_moderate'], vendor_data['job_counts_high']
    )

    permanent_visa_score = calculate_permanent_visa_score(
        {
            'certified': vendor_data['visa_certified_count'],
            'denied': vendor_data['visa_denied_count'],
            'withdrawn': vendor_data['visa_withdrawn_count'],
            'certified_expired': vendor_data['visa_certified_expired_count'],
            'unspecified': vendor_data['visa_unspecified_count'],
        },
        {
            'certified_trend': vendor_data['certified_trend'],
            'denied_withdrawn_trend': vendor_data['denied_withdrawn_trend']
        }
    )
    
    # combine scores using a weighted formula
    final_score = round(
        (adjusted_foreign_labor_score * 0.4) + (job_sensitivity_score * 0.3) + (permanent_visa_score * 0.3), 2
    )
    return final_score

# 8. interpretation of foreign labor risk
def interpret_foreign_labor_risk_score(score):
    if score >= 9.0:
        return "Low Risk", "Vendor has minimal reliance on foreign labor, low-risk roles, and favorable historical trend"
    elif 7.0 <= score < 9.0:
        return "Moderate Risk", "Vendor uses some foreign labor for low to moderately sensitive roles but demostrates reasonable controls."
    else:
        return "High Risk", "Vendor heavily relies on foreign labor, high-risk roles, or exhibits increasing dependence on H1-B."


# need pull interpretation of results by pulling each score interpretation into this function above