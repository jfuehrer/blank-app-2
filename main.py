import streamlit as st
from score_calculator import calculate_scores
from utils import load_and_validate_csv

def main():
    """Main function t load vendor data, calculate socres, and display results"""
    # define input csv path and required columns
    input_csv = "vendor_data.csv"
    required_columns = [
        'Vendor', 'Altman_Z', 'DTE', 'DTI', 'ROA',
        'Non-Fulfillment', 'Compliance', ' Adminstrative',
        'Agency Count', 'Sub-Agency Count', 'Growth Rate',
        'No Competition Percentage', 'foreign_labor_percentage',
        'country', 'job_counts_low', 'job_counts_moderate',
        'job_counts_high', 'visa_certified_count',
        'visa_denied_count', 'visa_withdrawn_count',
        'visa_unspecified_count', 'certified_trend', 'denied_withdrawn_trend'
    ]

    # load vendor data from CSV
    vendor_data = load_and_validate_csv(input_csv, required_columns)

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