import pandas as pd

# defined scoring critiera for each contract category
def score_amount_vs_year(growth_rate, fluctuation_type, drop_rate):
    if growth_rate > 10:
        return 10
    elif 6 <= growth_rate <=9:
        return 8
    elif 1 <= growth_rate <= 5:
        return 6
    elif fluctuation_type == 'minor':
        return 5
    elif fluctuation_type == 'moderate':
        return 4
    elif fluctuation_type == 'significant':
        return 3
    elif 1 <= drop_rate <= 9:
        return 2
    elif drop_rate > 10:
        return 1
    return 0

def score_amount_vs_agency(agency_count):
    if agency_count >= 5:
        return 10
    elif 3 <= agency_count <= 4:
        return 7
    elif 1 <= agency_count <= 2:
        return 4
    else:
        return 1
    
def score_amount_vs_sub_agency(sub_agency_count):
    if sub_agency_count >= 5:
        return 10
    elif 3 <= sub_agency_count <= 4:
        return 7
    elif 1 <= sub_agency_count <= 2:
        return 4
    else:
        return 1  
    
def score_amount_vs_competition(no_competition_percentage):
    if no_competition_percentage <= 10:
        return 10
    elif 11 <= no_competition_percentage <= 25:
        return 7
    elif 26 <= no_competition_percentage <= 50:
        return 4
    else:
        return 1
    
# This function calculates overall contract score based on weights
def calculate_contract_score(amount_vs_year_score, amount_vs_agency_score, amount_vs_sub_agency_score, amount_vs_competition_score):
    total_score = (amount_vs_year_score * 0.25) + \
    (amount_vs_agency_score * 0.25) + \
    (amount_vs_sub_agency_score * 0.25) + \
    (amount_vs_competition_score * 0.30)
    return round(total_score, 2)

# this functions will calculate and interpret the federal contract performance score
def calculate_federal_performance_score(amount_vs_year_score, amount_vs_agency_score, amount_vs_sub_agency_score, amount_vs_competition_score):
    performance_score = amount_vs_year_score + amount_vs_agency_score + amount_vs_sub_agency_score + amount_vs_competition_score
    if performance_score >= 8.0:
        return performance_score, "High Performance", "The company shows strong contractual growth, broad agency relationships, diverse sub-agency awards, and limited reliance on non-competitive contracts."
    elif 5.0 <= performance_score < 8.0:
        return performance_score, "Moderate Performance", "The company demonstrates solid performance but may need to improve diversification or reduce dependency on non-competitive contracts."
    else:
        return performance_score, "Low Performance", "The company has significant risks due to inconsistent growth, limited agency relationships, or high reliance on non-competitive awards."

# I don't know what the data Michael will provide so here is my current vendor data mockup example with metrics
vendor_data = [
    {
        "Vendor Name": "Vendor A",
        "Growth Rate": 12,
        "Fluctuation Type": "minor",
        "Drop Rate": 0,
        "Agency Count": 5,
        "Sub-Agency Count": 6,
        "No Competition Percentage": 9
    },
]

# initial thoughts on how to process each vendor and calcuate scores
results = []
for vendor in vendor_data:
    amount_vs_year_score = score_amount_vs_year(vendor['Growth Rate'], vendor['Fluctuation Type'], vendor['Drop Rate'])
    amount_vs_agency_score = score_amount_vs_agency(vendor['Agency Count'])
    amount_vs_sub_agency_score = score_amount_vs_sub_agency(vendor['Sub-Agency Count'])
    amount_vs_competition_score = score_amount_vs_competition(vendor['No Competition Percentage'])

    total_score = calculate_contract_score(amount_vs_year_score, amount_vs_agency_score, amount_vs_sub_agency_score, amount_vs_competition_score)
    performance_score, performance_category, interpretation = calculate_federal_performance_score(amount_vs_year_score, amount_vs_agency_score, amount_vs_sub_agency_score, amount_vs_competition_score)

    results.append({
        "Vendor Name": vendor['Vendor Name'],
        "Total Score": total_score,
        "Performance Score": performance_score,
        "Performance Category": performance_category,
        "Interpretation": interpretation
    })

    # create a dataframe for results
    results_df = pd.DataFrame(results)

    #output results to csv
    output_file = '/mnt/data/vendor_contract_scores_with_performance.csv'
    results_df.to_csv(output_file, index=False)

    output_file

# figure out the hooks this is api call placeholder
#def get_performance_score():
        # retrive the score from external API
        #response = requests.get("https://api.placeholder.com/score?vendor_id=123")
        #return response.json().get("performance_score")