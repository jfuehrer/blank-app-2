"""
Federal contract scoring module for the Vendor Risk Reliability Score (VRRS) application.
Calculates risk scores based on federal contract diversity and competition metrics.
"""

# List of codes for "Other Than Full and Open Competition"
OTHER_THAN_FULL_COMPETITION_CODES = ['ONE', 'NS', 'SP2', 'BND', 'IA', 'MES', 'UNQ', 'URG', 'OTH', 'RES', 'FOC', 'UR', 'PDR', 'UT', 'STD', 'PI', 'MPT']

# Agency diversity thresholds (higher number of agencies = lower risk)
AGENCY_THRESHOLDS = [
    (5, float('inf'), 1),  # 5+ agencies is very low risk
    (3, 4, 4),             # 3-4 agencies is low risk
    (1, 2, 7),             # 1-2 agencies is higher risk
    (0, 0, 10)             # 0 agencies is highest risk
]

# Sub-agency diversity thresholds
SUB_AGENCY_THRESHOLDS = [
    (5, float('inf'), 1),  # 5+ sub-agencies is very low risk
    (3, 4, 4),             # 3-4 sub-agencies is low risk
    (1, 2, 7),             # 1-2 sub-agencies is higher risk
    (0, 0, 10)             # 0 sub-agencies is highest risk
]

# Award type thresholds - higher values and prime contracts = lower risk
AWARD_TYPE_THRESHOLDS = {
    # Original award types
    'prime_contract': [
        (50_000_000, float('inf'), 1),
        (20_000_000, 50_000_000, 2),
        (10_000_000, 20_000_000, 3),
        (0, 10_000_000, 5)
    ],
    'prime_assistance': [
        (50_000_000, float('inf'), 2),
        (20_000_000, 50_000_000, 3),
        (10_000_000, 20_000_000, 4),
        (0, 10_000_000, 5)
    ],
    'sub_contract': [
        (50_000_000, float('inf'), 3),
        (20_000_000, 50_000_000, 4),
        (10_000_000, 20_000_000, 5),
        (0, 10_000_000, 6)
    ],
    'sub_assistance': [
        (50_000_000, float('inf'), 3),
        (20_000_000, 50_000_000, 4),
        (10_000_000, 20_000_000, 6),
        (0, 10_000_000, 7)
    ],
    
    # New dataset award types
    'prime_award': [
        (50_000_000, float('inf'), 1),
        (20_000_000, 50_000_000, 2),
        (10_000_000, 20_000_000, 3),
        (0, 10_000_000, 5)
    ],
    'sub_award': [
        (50_000_000, float('inf'), 3),
        (20_000_000, 50_000_000, 4),
        (10_000_000, 20_000_000, 5),
        (0, 10_000_000, 6)
    ],
    'sub-grant': [
        (50_000_000, float('inf'), 3),
        (20_000_000, 50_000_000, 4),
        (10_000_000, 20_000_000, 6),
        (0, 10_000_000, 7)
    ]
}

# Competition thresholds (higher non-competition % = higher risk)
COMPETITION_THRESHOLDS = [
    (0, 25, 1),            # 0-25% non-competitive is very low risk
    (26, 50, 4),           # 26-50% non-competitive is low risk
    (51, 70, 7),           # 51-70% non-competitive is medium risk
    (71, float('inf'), 10) # 71%+ non-competitive is high risk
]

def score_with_thresholds(value, thresholds):
    """
    Generic function to score based on value and predefined thresholds.
    
    Args:
        value (float): The value to score
        thresholds (list): List of (lower_bound, upper_bound, score) tuples
        
    Returns:
        int: The assigned score based on thresholds
    """
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0  # Default if no match

def score_amount_vs_year(award_type, amount):
    """
    Score award amount by type.
    
    Args:
        award_type (str): Type of award
        amount (float): Award amount
        
    Returns:
        int: Score based on award type and amount
    """
    return score_with_thresholds(amount, AWARD_TYPE_THRESHOLDS.get(award_type, []))

def score_amount_vs_competition(no_competition_percentage):
    """
    Score based on percentage of non-competitive awards.
    
    Args:
        no_competition_percentage (float): Percentage of non-competitive awards
        
    Returns:
        int: Score based on non-competition percentage
    """
    return score_with_thresholds(no_competition_percentage, COMPETITION_THRESHOLDS)

def score_amount_vs_agency(agency_count):
    """
    Score based on number of agencies served.
    
    Args:
        agency_count (int): Number of agencies served
        
    Returns:
        int: Score based on agency count
    """
    return score_with_thresholds(agency_count, AGENCY_THRESHOLDS)

def score_amount_vs_sub_agency(sub_agency_count):
    """
    Score based on number of sub-agencies served.
    
    Args:
        sub_agency_count (int): Number of sub-agencies served
        
    Returns:
        int: Score based on sub-agency count
    """
    return score_with_thresholds(sub_agency_count, SUB_AGENCY_THRESHOLDS)

def calculate_final_contract_score(vendor_data):
    """
    Calculate federal financial contract score normalized based on multiple criteria.
    
    Args:
        vendor_data (dict): Vendor data containing federal contract information
        
    Returns:
        float: Final normalized federal contract score
    """
    # Get the awards data, default to empty list if not present
    awards = vendor_data.get('awards', [])
    
    # If no awards, default to highest risk
    if not awards:
        awards = [{'type': 'prime_contract', 'amount': 0}]
    
    # Calculate amount vs year score for each award
    amount_vs_year_scores = [
        score_amount_vs_year(award.get('type', 'prime_contract'), award.get('amount', 0)) 
        for award in awards
    ]

    # Normalize by the number of awards
    normalized_amount_vs_year_score = (
        sum(amount_vs_year_scores) / len(amount_vs_year_scores) 
        if amount_vs_year_scores else 10
    )

    # Calculate other scores
    competition_score = score_amount_vs_competition(
        vendor_data.get('competition_percentage', 100)
    )
    agency_score = score_amount_vs_agency(
        vendor_data.get('agency_count', 0)
    )
    sub_agency_score = score_amount_vs_sub_agency(
        vendor_data.get('sub_agency_count', 0)
    )

    # Calculate the competition percentage using the competition codes
    if 'awards' in vendor_data and awards:
        total_awards = len(awards)
        non_competitive_awards = sum(
            1 for award in awards 
            if award.get('competition_code') in OTHER_THAN_FULL_COMPETITION_CODES
        )
        if total_awards > 0:
            competition_percentage = (non_competitive_awards / total_awards) * 100
            competition_score = score_amount_vs_competition(competition_percentage)
            # Store these values for visualization
            vendor_data['competition_percentage'] = competition_percentage
            vendor_data['competition_score'] = competition_score
            vendor_data['non_competitive_awards'] = non_competitive_awards
            vendor_data['total_awards'] = total_awards

    # Store component scores for visualization
    vendor_data['agency_score'] = agency_score
    vendor_data['sub_agency_score'] = sub_agency_score
    vendor_data['normalized_amount_vs_year_score'] = normalized_amount_vs_year_score

    # Apply weighted formula to calculate the final score
    total_score = (
        (agency_score * 0.25) +
        (sub_agency_score * 0.20) +
        (normalized_amount_vs_year_score * 0.25) +
        (competition_score * 0.30)
    )

    return round(total_score, 2)

def interpret_federal_contract_score(score):
    """
    Interpret the final federal contract performance score.
    
    Args:
        score (float): The federal contract score
        
    Returns:
        tuple: (risk_category, interpretation_message)
    """
    # Aligned with VRRS thresholds for consistency
    if score >= 8.0:
        return "Severe Risk", "The company has critical issues with contract growth, extremely limited agency relationships, and almost exclusive reliance on non-competitive awards."
    elif 6.5 <= score < 8.0:
        return "High Risk", "The company has significant risks due to inconsistent growth, limited agency relationships, or high reliance on non-competitive awards."
    elif 4.5 <= score < 6.5:
        return "Moderate Risk", "The company demonstrates average performance but needs to improve diversification and reduce dependency on non-competitive contracts."
    elif 2.5 <= score < 4.5:
        return "Low Risk", "The company demonstrates solid contract performance with satisfactory diversification across agencies."
    else:
        return "Very Low Risk", "The company shows strong contractual growth, broad agency relationships, diverse sub-agency awards, and limited reliance on non-competitive contracts."