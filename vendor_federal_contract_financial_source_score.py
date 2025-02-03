import pandas as pd

# call to utils function to load and validate csv
from utils import load_and_validate_csv

data = load_and_validate_csv('federal_contract_financial_source_data.csv', ['amount_vs_year', 'growth_rate', 'amount_vs_agency', 'amount_vs_sub_agency', 'amount_vs_competition'])


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

# the function to valide required columns in CSV file
def validate_csv_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
# the function to process data from csv file
def process_csv_file(input_csv):
    """Load CSV file, validate columns, and calculate scores"""
    required_columns = [
        'Vendor Name', 'Growth Rate', 'Fluctuation Type', 'Drop Rate',
        'Agency Count', 'Sub-Agency Count', 'No Competition Percentage'
    ]

    # Load CSV File
    df = pd.read.csv(input_csv)

    # Then validate csv file for required columns
    validate_csv_columns(df, required_columns)

    # Function to calculate score for each vendor
    
    results = []
    for _, row in df.iterrows():
        amount_vs_year_score = score_amount_vs_year(row['Growth Rate'], row['Fluctuation Type'], row['Drop Rate'])
        amount_vs_agency_score = score_amount_vs_agency(row['Agency Count'])
        amount_vs_sub_agency_score = score_amount_vs_sub_agency(row['Sub-Agency Count'])
        amount_vs_competition_score = score_amount_vs_competition(row['No Competition Percentage'])
        
        total_score = calculate_contract_score(amount_vs_year_score, amount_vs_agency_score, amount_vs_sub_agency_score, amount_vs_competition_score)
        performance_score, performance_category, interpretation = calculate_federal_performance_score(amount_vs_year_score, amount_vs_agency_score, amount_vs_sub_agency_score, amount_vs_competition_score)
        
        results.append({
            "Vendor Name": row['Vendor Name'],
            "Total Score": total_score,
            "Performance Score": performance_score,
            "Performance Category": performance_category,
            "Interpretation": interpretation
        })

    # create a dataframe for results
    results_df = pd.DataFrame(results)
    return results_df

# example usage
input_csv_file = '/mnt/data/vendor_contract_financial_source_input.csv'
output_csv_file = '/mnt/data/vendor_contract_financial_source_scores.csv'

# process csv and export results

try:
    results_df = process_csv_file(input_csv_file)
    results_df.to_csv(output_csv_file, index=False)
    print(f"Results saved {output_csv_file}")
except Exception as e:
    print(f"Error process CSV file: {e}")

output_csv_file