import pandas as pd

# define scoring critera
def get_cancellation_score(cancellation_type, count):
    """Determine score based on te number of cancellations for a given type."""
    if cancellation_type == "Non-Fulfillment":
        if count == 0:
            return 10
        elif count == 1:
            return 5
        else:
            return 1
    elif cancellation_type == "Compliance":
        if count == 0:
            return 10
        elif count == 1:
            return 7
        else:
            return 1
    elif cancellation_type == "Adminstrative":
        if count == 0:
            return 10
        elif count == 1:
            return 8
        else:
            return 5
        
# This is the function to calculate past performance score. See Jeff's comments in slides for extending for v2
def calculate_past_performance_score(non_fulfillment, compliance, adminstrative):
    """Calculate the overall past performance score based on cancellation data."""
    non_fulfillment_score = get_cancellation_score("Non-Fulfillment", non_fulfillment)
    compliance_score = get_cancellation_score("Compliance", compliance)
    adminstrative_score = get_cancellation_score("Adminstrative", adminstrative)

    # Apply weighted formula for the final risk score
    cancellation_risk_score = (non_fulfillment_score * 0.50) + (compliance_score * 0.35) + (adminstrative_score * 0.15)
    return cancellation_risk_score

# This is the function to process data from a CSV file and calculate scores
def process_vendor_data(input_csv, output_csv):
    """Read vendor data from CSV, calculate past performance scores, and save results."""
    # Read input CSV
    vendor_data = pd.read_csv(input_csv)

    #calculate scores for each vendor
    results = []
    for _, row in vendor_data.iterrows():
        score = calculate_past_performance_score(row['Non-Fulfillment'], row['Compliance'], row['Adminstrative'])
        results.append({
            "Vendor Name": row['Vendor Name'],
            "Score": round(score, 2)
        })
    
    # Create a dataframe for results
    results_df = pd.DataFrame(results)

    # Export results in CSV
    results_df.to.csv(output_csv, index=False)
    return output_csv

# Josh remember to setup paths-the following is example usage
input_csv_file = '/mnt/data/vendor_cancellation_data.csv' #Josh remember to replace with actual path to input file. Check with Ben on how they are doing it and replicate
output_csv_file = '/mnt/data/vendor_past_performance_results.csv'

# Josh remember- Uncomment to run after providing the input file
# process_vendor_data(input_csv_file, output_csv_file)

output_csv_file

# figure out the hooks this is api call placeholder
#def get_cancellation_risk_score():
        # retrive the score from external API
        #response = requests.get("https://api.placeholder.com/score?vendor_id=123")
        #return response.json().get("get_cancellation_risk_score")