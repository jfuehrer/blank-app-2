# # Josh note: foreign labor score is working and has been tested.
# josh additional note: need to relook at foreign percentage and possibly remove and focus on counts. Palo alto run looked funny.
# josh additional additional note: need to look at trend scoring and remove just focus on current year--removed trend
# updated reversal based on blue/cabby comments

# foreign labor scoring
COUNTRY_RISK_MULTIPLIER = {
    'low_risk': 0.6,
    'moderate_risk': 0.8,
    'high_risk': 1.0
}

RISK_CATEGORIZATION = {
    'low_risk': ['USA', 'Canada', 'Germany', 'France'],
    'moderate_risk': ['India', 'Brazil', 'South Korea'],
    'high_risk': ['Russia', 'China', 'Iran']   
}

VISA_CATEGORY_THRESHOLDS = {
    'certified': [
        (0, 10, 1), 
        (11, 20, 6), 
        (21, 50, 8), 
        (51, float('inf'), 10)
    ],
    'denied': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ],
    'withdrawn': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ],
    'certified_expired': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ],
    'unspecified': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ]
}

# removed 
#FOREIGN_LABOR_PERCENTAGE_THRESHOLDS = [
#    (0, 0, 10), #0% foreign labor receives a perfect score
#    (1, 10, 8), #1% to 10% foreign labor gets a score of 8
#    (11, 20, 6), # 11% to 20% foreign labor gets a score of 6 
#    (21, 50, 4), # 21% to 50% foreign labor gets a score of 4
#    (51, float('inf'), 2) # Greate than 50% gets a score of 2
#]


#removed
#TREND_ADJUSTMENT = {
#    'favorable': 2,
#    'neutral': 6,
#    'unfavorable': 10
#}


# 0. generic scoring function based on thresholds
def score_with_thresholds(value, thresholds):
    """Score a values based on predefined thresholds"""
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0

# 1. Country risk multipler
def get_country_risk_multiplier(country):
    """Get the risk multipler based on the country."""
    for risk_level, countries in RISK_CATEGORIZATION.items():
        if country in countries:
            return COUNTRY_RISK_MULTIPLIER[risk_level]
    return COUNTRY_RISK_MULTIPLIER['moderate_risk']

# 2. Visa Category Score
def get_visa_category_score(category, count):
   """Calculate the score for a specific visa category based on counts"""
   return score_with_thresholds(count, VISA_CATEGORY_THRESHOLDS.get(category, []))

# 3. Job Sensitivity Score
def calculate_job_sensitivity_score(low, moderate, high):
    """Calculate the job sensitivity score based on the number of job types"""
    total_jobs = low + moderate + high
    if total_jobs == 0:
        return 1 # no freign labor means minimal job risk
    
    weighted_score = ((low * 1) + (moderate * 6) + (high * 10)) / total_jobs
    return weighted_score

# 4 calculate country score
def calculate_country_score_with_visa(country_data, visa_counts):
    """Calculate the foreign labor score for a specific country
    :param country_data: dictionary with country and job sensitivity counts 
    :param visa_counts: dictionary with visa category counts.
    """
    country = country_data['country']
    low_sensitivity_count = country_data.get('job_counts_low', 0)
    moderate_sensitivity_count = country_data.get('job_counts_moderate', 0)
    high_sensitivity_count = country_data.get('job_counts_high', 0)

    # get the country risk multiplier
    risk_multiplier = get_country_risk_multiplier(country)

    # calculate the job sensitivity score
    job_sensitivity_score = calculate_job_sensitivity_score(
        low_sensitivity_count, moderate_sensitivity_count, high_sensitivity_count
    )

    # calculate base visa score and normalize categories
    total_visa_score = sum(get_visa_category_score(category, count) for category, count in visa_counts.items())
    normalized_visa_score = total_visa_score / len(visa_counts)

    # apply the country risk multiplier and weight (0.5) to visa score)
    adjusted_visa_score = normalized_visa_score * risk_multiplier

    # combine job sensitivity score and adjust visa score
    final_country_score = (job_sensitivity_score * 0.40) + (adjusted_visa_score * 0.60)
    final_country_score = min(max(final_country_score, 0), 10)
    return final_country_score

# 5 calculate final adjusted foreign labor score

def calculate_final_adjusted_foreign_labor_score(countries_data, visa_counts):
    """
    Calculate the final adjusted foreign labor score across multiple countries
    :param countries_data: list of country data
    :param visa_counts: Dictionary with visa counts
    """
    if not countries_data:
        return 0 # no foreign labor data
    
    # calculate scores for each country and average them
    country_scores = [
        calculate_country_score_with_visa(country_data, visa_counts) for country_data in countries_data
    ]
    # normalize the score by diving by the number of countries
    total_score = sum(country_scores) 
    normalized_score = total_score / len(countries_data)

    return round(normalized_score, 2)

'''
# 6 calcluate visa trend score - removed
def calculate_visa_trend_score(trend_data):
    """calculate a score based on recent trends"""
    if trend_data['denied_withdrawn_trend'] == 10 or trend_data['certified_trend'] == 10:
        return TREND_ADJUSTMENT['favorable']
    elif trend_data['certified_trend'] == 6 and trend_data['denied_withdrawn_trend'] == 6:
        return TREND_ADJUSTMENT['neutral']
    else:
        return TREND_ADJUSTMENT['unfavorable']
'''

# Josh: Need to confirm weighting is applied correctly

# 7. Final Foreign Labor Risk Score
def calculate_final_foreign_labor_score(vendor_data):
    """Calculate the final foreign labor score for a vendor
    :param vendor_data: dictionary containing all relevant vendor information
    """
    #1. adjust foreign labor score with visa impact
    countries_data = vendor_data.get('countries_data', [])
    visa_counts = {
        'certified': vendor_data.get('visa_certified_count', 0),
        'denied': vendor_data.get('visa_denied_count', 0),
        'withdrawn': vendor_data.get('visa_withdrawn_count', 0),
        'certified_expired': vendor_data.get('visa_certified_expired_count', 0),
        'unspecified': vendor_data.get('visa_unspecified_count', 0)
    }
    adjusted_foreign_labor_score = calculate_final_adjusted_foreign_labor_score(countries_data, visa_counts)

    # visa trend score
    #trend_data = {
    #    'certified_trend': vendor_data['certified_trend'],
    #    'denied_withdrawn_trend': vendor_data['denied_withdrawn_trend']  
    #}
    #visa_trend_score = calculate_visa_trend_score(trend_data)
 
    # final risk score calculation using a weighted formula
    final_score = adjusted_foreign_labor_score 
    return round(final_score, 2)

# 8. interpretation of foreign labor risk
def interpret_foreign_labor_risk_score(score):
    if score >= 4.0:
        return "High Risk", "Vendor heavily relies on foreign labor, high-risk roles, or exhibits increasing dependence on H1-B."
    elif 2.0 <= score < 3.9:
        return "Moderate Risk", "Vendor uses some foreign labor for low to moderately sensitive roles but demostrates reasonable controls."
    else:
        return "Low Risk", "Vendor has minimal reliance on foreign labor, low-risk roles, and favorable historical trend."



# need pull interpretation of results by pulling each score interpretation into this function above