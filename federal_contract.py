# federal contract financial scoring
AGENCY_COUNT_THRESHOLDS = [
    (5, float('inf'), 10),
    (3, 4, 7),
    (1, 2, 4),
    (0, 0, 1)
]

SUB_AGENCY_COUNT_THRESHOLDS = [
    (5, float('inf'), 10),
    (3, 4, 7),
    (1, 2, 4),
    (0, 0, 1)
]

GROWTH_RATE_THRESHOLDS = [
    (10, float('inf'), 10),
    (6, 9, 8),
    (1, 5, 6),
    (-float('int'), 0, 3) # negative growth scores lower
]

NO_COMPETITION_THRESHOLDS = [
    (0, 10, 10),
    (11, 25, 7),
    (26, 50, 4),
    (51, float('inf'), 1)
]

def score_with_thresholds(value, thresholds):
    """Generic function to score based on value and predefined thresholds."""
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0

# individual scoring functions
def score_amount_vs_agency(agency_count):
    return score_with_thresholds(agency_count, AGENCY_COUNT_THRESHOLDS)

def score_amount_vs_sub_agency(sub_agency_count):
    return score_with_thresholds(sub_agency_count, SUB_AGENCY_COUNT_THRESHOLDS)

def score_amount_vs_growth_rate(growth_rate):
    return score_with_thresholds(growth_rate, GROWTH_RATE_THRESHOLDS)

def score_amount_vs_competition(no_competition_percentage):
    return score_with_thresholds(no_competition_percentage, NO_COMPETITION_THRESHOLDS)

# main function to calculate federal contract financial score
def get_federal_contract_score(vendor_data):
    """calculate federal financial contract score based on multiple critiera"""
    agency_score = score_amount_vs_agency(vendor_data['Agency Count'])
    sub_agency_score = score_amount_vs_sub_agency(vendor_data['Sub_Agency Count'])
    growth_rate_score = score_amount_vs_growth_rate(vendor_data['Growth Rate'])
    competition_score = score_amount_vs_competition(vendor_data['No Competition Percentage'])

    #applied weighted formulate to calculate the final score
    total_score = (
        (agency_score * 0.25) +
        (sub_agency_score * 0.25) +
        (growth_rate_score * 0.20) +
        (competition_score * 0.30)
    )

    return round(total_score, 2)

# interpretation function
def interpret_federal_contract_score(score):
    """Interpret the final federal contract performance score"""
    if score >= 8.0:
        return "High Performance", "The company shows strong contractual growth, broad agency relationships, diverse sub-agency awards, and limited reliance on non-competitive contracts."
    elif 5.0 <= score < 8.0:
        return "Moderate Performance", "The company demonstrates solid performance but may need to improve diversification or reduce dependency on non-competitive contracts."
    else:
        return "Low Performance", "The company has significant risks due to inconsistent growth, limited agency relationships, or high reliance on non-competitive awards."