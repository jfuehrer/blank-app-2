# Josh note: federal contract score is working and has been tested.
# scoring reversed to meet cabby/blue ask

# federal contract financial scoring
AGENCY_THRESHOLDS = [
    (5, float('inf'), 1),
    (3, 4, 4),
    (1, 2, 7),
    (0, 0, 10)
]

SUB_AGENCY_THRESHOLDS = [
    (5, float('inf'), 1),
    (3, 4, 4),
    (1, 2, 7),
    (0, 0, 10)
]

AWARD_TYPE_THRESHOLDS = {
    'prime_contract': [(50_000_000, float('inf'), 1), (20_000_000, 50_000_000, 2), (10_000_000, 20_000_000, 3), (0, 10_000_000, 5)],
    'prime_assistance': [(50_000_000, float('inf'), 2), (20_000_000, 50_000_000, 3), (10_000_000, 20_000_000, 4), (0, 10_000_000, 5)],
    'sub_contract': [(50_000_000, float('inf'), 3), (20_000_000, 50_000_000, 4), (10_000_000, 20_000_000, 5), (0, 10_000_000, 6)],
    'sub_assistance': [(50_000_000, float('inf'), 3), (20_000_000, 50_000_000, 4), (10_000_000, 20_000_000, 6), (0, 10_000_000, 7)],
}

COMPETITION_THRESHOLDS = [
    (0, 10, 1),
    (11, 25, 4),
    (26, 50, 7),
    (51, float('inf'), 10)
]

def score_with_thresholds(value, thresholds):
    """Generic function to score based on value and predefined thresholds."""
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0

# individual scoring functions
def score_amount_vs_year(award_type, amount):
    return score_with_thresholds(amount, AWARD_TYPE_THRESHOLDS.get(award_type, []))

def score_amount_vs_competition(no_competition_percentage):
    return score_with_thresholds(no_competition_percentage, COMPETITION_THRESHOLDS)

def score_amount_vs_agency(agency_count):
    return score_with_thresholds(agency_count, AGENCY_THRESHOLDS)

def score_amount_vs_sub_agency(sub_agency_count):
    return score_with_thresholds(sub_agency_count, SUB_AGENCY_THRESHOLDS)

# main function to calculate federal contract financial score
def calculate_final_contract_score(vendor_data):
    """calculate federal financial contract score normalized based on multiple critiera
    :param awards: List of dictionaries with award details
    :param competition: Percentage of contracts awarded without competition
    :param agency_count: Number of agencies served by the vendor
    :param sub_agency count: Number of sub-agencies served by the vendor
    :return: final normalized score
    """
    # calculate amount vs year score for each award
    awards = vendor_data['awards']
    amount_vs_year_scores = [score_amount_vs_year(award['type'], award['amount']) for award in awards]

    # normalize by the number of awards
    normalized_amount_vs_year_score = sum(amount_vs_year_scores) / len(amount_vs_year_scores) if amount_vs_year_scores else 10

    # calculate other scores
    competition_score = score_amount_vs_competition(vendor_data['competition_percentage'])
    agency_score = score_amount_vs_agency(vendor_data['agency_count'])
    sub_agency_score = score_amount_vs_sub_agency(vendor_data['sub_agency_count'])

    #applied weighted formulate to calculate the final score
    total_score = (
        (agency_score * 0.25) +
        (sub_agency_score * 0.20) +
        (normalized_amount_vs_year_score * 0.25) +
        (competition_score * 0.30)
    )

    return round(total_score, 2)


# interpretation function
def interpret_federal_contract_score(score):
    """Interpret the final federal contract performance score"""
    if score >= 5.0:
        return "Low Performance", "The company has significant risks due to inconsistent growth, limited agency relationships, or high reliance on non-competitive awards."
    elif 2.0 <= score < 4.9:
        return "Moderate Performance", "The company demonstrates solid performance but may need to improve diversification or reduce dependency on non-competitive contracts."
    else:
        return "High Performance", "The company shows strong contractual growth, broad agency relationships, diverse sub-agency awards, and limited reliance on non-competitive contracts."
