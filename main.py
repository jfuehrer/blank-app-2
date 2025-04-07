import streamlit as st
import pandas as pd
from score_calculator import calculate_scores
from utils import fetch_vendor_data

def main():
    """Main function t load vendor data, calculate socres, and display results"""
    # define input csv path and required columns
    vendor_id = "vendor123"
    vendor_data = fetch_vendor_data(vendor_id)

    results = calculate_scores(vendor_data)
    print("Vendor Risk Reliability Score Report:")
    for key, value in results.items():
        print(f"{key}: {value}")
    
    

    # calculate scores for each vendor
    results = []
    for _, row in vendor_data.iterrows():
        results = calculate_scores(row)
        results['Vendor'] = row['Vendor']
        results.append(results)

    # display results
    print("\nVendor:", results['Vendor'])
    for key, value in results.items():
        if key != 'Vendor':
            print(f"{key}: {value}")

    # save results to csv
    output_csv = "vendor_risk_scores_report.csv"
    save_results_to_csv(results, output_csv)
    print(f"\nResults saved to {output_csv}")

# Ben: You would write your visualization here OR branch it out from the main file.
# Ben: best way to do it, calculations first, then visualization

def save_results_to_csv(results, output_file):
    """Save results to csv file"""
    import pandas as pd
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()