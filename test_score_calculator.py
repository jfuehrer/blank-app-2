from score_calculator import calculate_scores

# sample vendor data
vendor_data_example = {
    'Altman_Z': 3.5,
    'DTE': 1.2,
    'DTI': 0.8,
    'ROA': 0.15,
    'ROE': 0.12,
    'Non-Fulfillment': 1,
    'Compliance': 0,
    'Adminstrative': 2,
    'Agency Count': 4,
    'Sub-Agency Count': 3,
    'Growth Rate': 7,
    'No Competition Percentage': 20,
    'foreign_labor_percentage': 15,
    'country': 'India',
    'job_counts_low': 20,
    'job_counts_moderate': 10,
    'job_counts_moderate': 10,
    'job_counts_high': 5,
    'visa_certified_count': 25,
    'visa_denied_count': 5,
    'visa_withdrawn_count': 2,
    'visa_unspecified_count': 0,
    'certified_trend': 'stable',
    'denied_withdrawn_trend': 'upward'
}

#calculate and display scores
results = calculate_scores(vendor_data_example)

print("Vendor Risk Reliability Score Report:")
for key, value in results.items():
    print(f"{key}: {value}")