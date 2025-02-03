# this handles orchestration by invoking each scoring function and combing their results

# import functions from other modules
from financial_stability import get_financial_stability_score
from past_performance import get_past_performance_score
from federal_contract import get_federal_contract_score
from foreign_labor import calculate_final_foreign_labor_score
from risk_categories import determine_risk_category

def calculate_vendor_risk_reliability(financial, past, contract, labor):
    """Example formulate for calculating the final vendor risk relaiblity score"""
    return round((financial * 0.3) + (past * 0.3) + (contract * 0.2) +(labor * 0.2), 2)

def calculate_scores(vendor_data):
    """Calculate all vendor scores and return a comphrensive result dictionary"""
    financial_stability_score = get_financial_stability_score(vendor_data)
    past_performance_score = get_past_performance_score(vendor_data)
    federal_contract_score = get_federal_contract_score(vendor_data)
    foreign_labor_score = calculate_final_foreign_labor_score(vendor_data)

    #calculate final VRRS score
    vrrs_score = calculate_vendor_risk_reliability(
        financial_stability_score,
        past_performance_score,
        federal_contract_score,
        foreign_labor_score
    )

    # interpret the VRRS score
    risk_category, interpretation = determine_risk_category(vrrs_score)

    return {
        "financial_stability_score": financial_stability_score,
        "past_performance_score": past_performance_score,
        "federal_contract_score": federal_contract_score,
        "foreign_labor_score": foreign_labor_score,
        "vrrs_score": vrrs_score,
        "risk_category": risk_category,
        "interpretation": interpretation
    }
