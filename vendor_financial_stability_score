import pandas as pd

# Load CSV file ('replace financial_data_csv') with your file name) make sure to confirm name and headers
data = pd.read_csv('financial_data.csv')

# josh ensure the csv contains the required columns
required_columns = ['Vendor', 'Altman_Z', 'DTE', 'ROA', 'ROE']
for col in required_columns:
    if col not in data.columns:
        raise ValueError(f"Missing required column: {col}")
    
# define weightings for each FM
weights = {
    'Altman_Z': 0.30,
    'DTE': 0.20,
    'DTI': 0.20,
    'ROA': 0.15,
    'ROE': 0.15
}

# function to calculate the financial stability score
def calculate_financial_score(row):
    weighted_score = (
        (row['Altman_Z'] * weights['Altman_Z']) +
        (row['DTE'] * weights['DTE']) +
        (row['DTI'] * weights['DTI']) +
        (row['ROA'] * weights['ROA']) +
        (row['ROE'] * weights['ROE'])
    )
    # normalize by dividing by the sum of the weights
    return weighted_score / sum(weights.values())

# function to determine the financial risk category and interpretation
def determine_risk_category(score):
    if score >= 8.0:
        return 'Low Risk', 'Strong financial health, reliable vendor. Proceed with confidence.'
    elif 6.0 <= score < 8.0:
        return 'Moderate Risk', 'Stable, moderate financial health.'
    elif 4.0 <= score < 6.0:
        return 'High Risk', 'Poor financial health; high-risk vendor. Consider alternative or monitor closely. Proceed cautiously'
    else:
        return 'Severe Risk', 'Potential bankruptcy or major financial distress. Avoid vendor'
    
# Apply the function to each row to calculate the score and risk category
data['Financial_stability_score'] = data.apply(calculate_financial_score, axis=1)
data[['Risk_Category', 'Interpretation']] = data['Financial_stability_score'].apply(lambda score: pd.Series(determine_risk_category(score)))

# Display the results
print(data[['Vendor', 'Financial_Stability_Score', 'Risk_Category', 'Interpretation']])

# Save the results to a new CSV File
data.to.csv('financial_stability_scores_with_risk.csv', index=False)