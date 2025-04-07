"""
Financial stability scoring module for the Vendor Risk Reliability Score (VRRS) application.
Calculates risk scores based on financial health metrics like Altman Z-score, debt ratios, and returns.
Now includes both point-in-time scoring and historical trend analysis.
"""
import pandas as pd
from scipy import stats

# Financial stability scoring metric weights - point-in-time assessment
FINANCIAL_METRIC_WEIGHTS = {
    'Altman_Z': 0.30,
    'DTE': 0.20,
    'DTI': 0.20,
    'ROA': 0.15,
    'ROE': 0.15
}

# Scoring thresholds for each financial metric - point-in-time assessment
METRIC_RANGES = {
    'Altman_Z': [
        (1.0, 1.81, 10),  # Higher score means higher risk
        (1.81, 2.99, 5), 
        (2.99, float('inf'), 1)
    ],
    'DTE': [
        (0.0, 0.5, 1), 
        (0.51, 1.0, 3), 
        (1.01, 2.00, 5), 
        (2.01, 3.0, 7), 
        (3, float('inf'), 10)
    ],
    'DTI': [
        (0.0, 0.5, 1), 
        (0.51, 1.0, 3), 
        (1.01, 2.00, 5), 
        (2.01, 3.0, 7), 
        (3, float('inf'), 10)
    ],
    'ROA': [
        (-1.0, -0.50, 10), 
        (-0.49, -0.01, 8),
        (0.0, 0.50, 5),
        (0.51, 0.99, 3),
        (1.0, float('inf'), 1)
    ],
    'ROE': [
        (-1.0, -0.50, 10), 
        (-0.49, -0.01, 8),
        (0.0, 0.50, 5),
        (0.51, 0.99, 3),
        (1.0, float('inf'), 1)
    ]
}

# Scoring for historical trends
TREND_SCORES = {
    # For ROA, ROE, Altman Z-Score: positive trend = lower risk
    'ROA': {'improving': 2, 'stable': 5, 'declining': 10},
    'ROE': {'improving': 2, 'stable': 5, 'declining': 10},
    'Altman_Z': {'improving': 2, 'stable': 5, 'declining': 10},

    # For debt ratios: negative trend = lower risk
    'DTE': {'improving': 10, 'stable': 5, 'declining': 2},
    'DTI': {'improving': 10, 'stable': 5, 'declining': 2}
}

# Map Excel column names to internal keys
EXCEL_TO_INTERNAL_KEYS = {
    'Altman Z-Score': 'Altman_Z',
    'Debt-to-Equity Ratio': 'DTE',
    'Debt-to-Income Ratio': 'DTI',
    'Return on Assets': 'ROA',
    'Return on Equity': 'ROE'
}

def score_with_thresholds(value, thresholds):
    """
    Assigns a score based on predefined thresholds.

    Args:
        value (float): The metric value to score
        thresholds (list): List of (lower_bound, upper_bound, score) tuples

    Returns:
        int: The assigned score based on thresholds
    """
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0  # Default score if no match is found


def calculate_financial_metric_score(metric, value):
    """
    Calculate the financial metric score based on predefined thresholds.

    Args:
        metric (str): The name of the financial metric
        value (float): The value of the financial metric

    Returns:
        int: Score assigned to the metric value
    """
    return score_with_thresholds(value, METRIC_RANGES.get(metric, []))


def analyze_trend(years, values, metric):
    """
    Calculate the trend for a given metric using linear regression and classify as improving, stable, or declining.
    Enhanced with more sophisticated trend detection and more accurate regression analysis.

    Args:
        years (list): List of years as numeric values
        values (list): List of metric values
        metric (str): The name of the metric being analyzed

    Returns:
        dict: Contains trend classification and slope information
    """
    # Need at least 2 data points to calculate a trend
    if len(years) < 2 or len(values) < 2:
        return {'trend': 'stable', 'slope': 0, 'score': TREND_SCORES[metric]['stable']}

    # Clean data - remove any NaN values by pairing years and values
    valid_data = [(y, v) for y, v in zip(years, values) if not pd.isna(v)]
    if len(valid_data) < 2:
        return {'trend': 'stable', 'slope': 0, 'score': TREND_SCORES[metric]['stable']}

    # Unpack the valid data pairs
    cleaned_years, cleaned_values = zip(*valid_data)
    
    # Sort data by year to ensure correct trend analysis
    sorted_data = sorted(zip(cleaned_years, cleaned_values))
    cleaned_years, cleaned_values = zip(*sorted_data)
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(cleaned_years, cleaned_values)
    
    # Calculate relative change (percentage) instead of absolute for better comparison
    if len(cleaned_values) >= 2:
        first_value = cleaned_values[0]
        last_value = cleaned_values[-1]
        
        # Prevent division by zero
        if first_value != 0:
            relative_change = (last_value - first_value) / abs(first_value)
        else:
            relative_change = 0 if last_value == 0 else 1 if last_value > 0 else -1
    else:
        relative_change = 0

    # More sophisticated significance criteria
    # 1. Statistical significance via p-value
    # 2. Practical significance via R-squared (correlation strength)
    # 3. Magnitude significance via relative change
    statistical_sig = p_value < 0.05
    correlation_sig = abs(r_value) > 0.5
    
    # Magnitude significance thresholds vary by metric
    if metric in ['ROA', 'ROE']:
        # These metrics are percentages, so smaller changes matter
        magnitude_sig = abs(relative_change) > 0.15
    elif metric == 'Altman_Z':
        # For Z-score, changes above 0.2 are significant
        magnitude_sig = abs(relative_change) > 0.2
    else:  # Debt ratios
        # For debt ratios, larger changes needed to be significant
        magnitude_sig = abs(relative_change) > 0.25
    
    # A trend is significant if it's statistically significant or has both correlation and magnitude significance
    significant = statistical_sig or (correlation_sig and magnitude_sig)
    
    # For very short time series (2-3 points), rely more on magnitude than statistics
    if len(cleaned_years) <= 3:
        significant = significant or abs(relative_change) > 0.3
    
    # Classify trend
    if not significant:
        trend = 'stable'
    else:
        # For ROA, ROE, Altman Z-Score, positive slope is improvement
        # For debt ratios, negative slope is improvement
        if metric in ['ROA', 'ROE', 'Altman_Z']:
            trend = 'improving' if slope > 0 else 'declining'
        else:  # DTE, DTI
            trend = 'improving' if slope < 0 else 'declining'

    # Assign score based on trend
    score = TREND_SCORES[metric][trend]

    # Return more comprehensive trend information with enhanced visualization properties
    return {
        'trend': trend,
        'slope': slope,
        'intercept': intercept,
        'p_value': p_value,
        'r_squared': r_value**2,
        'std_err': std_err,
        'statistical_sig': statistical_sig,
        'correlation_sig': correlation_sig,
        'magnitude_sig': magnitude_sig,
        'relative_change': relative_change,
        'significance': significant,
        'score': score,
        'classification': trend,  # Include classification field for consistency
        'data_points': len(cleaned_years),
        'first_value': cleaned_values[0] if cleaned_values else None,
        'last_value': cleaned_values[-1] if cleaned_values else None,
        # Add visualization helper properties
        'direction': 'up' if (metric in ['ROA', 'ROE', 'Altman_Z'] and slope > 0) or 
                           (metric not in ['ROA', 'ROE', 'Altman_Z'] and slope < 0) else 'down',
        'color': 'green' if trend == 'improving' else 'orange' if trend == 'stable' else 'red',
        'symbol': '↑' if (metric in ['ROA', 'ROE', 'Altman_Z'] and slope > 0) or 
                         (metric not in ['ROA', 'ROE', 'Altman_Z'] and slope < 0) else '→' 
                         if trend == 'stable' else '↓'
    }


def calculate_trend_score(financial_data):
    """
    Calculate historical trend scores for financial metrics.

    Args:
        financial_data (dict): Dictionary containing historical financial data with years as keys

    Returns:
        tuple: (trend_score, trend_details) - overall trend score and detailed breakdown
    """
    # Check if historical data is in the expected format
    if not isinstance(financial_data, dict) or not financial_data:
        return 5.0, {}  # Default to moderate risk if no data

    # Print debug info about financial_data
    print(f"Historical financial data to analyze: {len(financial_data)} years of data")

    # Organize data by metric
    metrics_data = {
        'Altman_Z': {'years': [], 'values': []},
        'DTE': {'years': [], 'values': []},
        'DTI': {'years': [], 'values': []},
        'ROA': {'years': [], 'values': []},
        'ROE': {'years': [], 'values': []}
    }

    # Collect data for each metric across years
    for year, metrics in sorted(financial_data.items()):
        try:
            year_num = int(year)
            for metric in metrics_data:
                if metric in metrics and metrics[metric] is not None:
                    try:
                        value = float(metrics[metric])
                        metrics_data[metric]['years'].append(year_num)
                        metrics_data[metric]['values'].append(value)
                    except (ValueError, TypeError):
                        print(f"Could not convert {metrics[metric]} to float for {metric} in year {year}")
                        pass
        except (ValueError, TypeError):
            print(f"Could not process year {year}")
            continue

    # Analyze trend for each metric
    trend_results = {}
    trend_scores = {}

    for metric, data in metrics_data.items():
        if data['years'] and data['values']:
            print(f"Analyzing trend for {metric}: {len(data['years'])} data points")
            trend_analysis = analyze_trend(data['years'], data['values'], metric)
            trend_results[metric] = trend_analysis
            trend_scores[metric] = trend_analysis['score']
        else:
            print(f"No trend data available for {metric}")

    # Calculate weighted score if we have any trend data
    if trend_scores:
        # Normalize each trend score to 1-10 scale before applying weights
        normalized_trend_scores = {}
        for metric in FINANCIAL_METRIC_WEIGHTS:
            score = trend_scores.get(metric, 5)
            # Ensure score is within 1-10 range
            normalized_score = max(1, min(10, score))
            normalized_trend_scores[metric] = normalized_score

        # Calculate weighted average using normalized scores
        weighted_trend_score = sum(
            normalized_trend_scores[metric] * FINANCIAL_METRIC_WEIGHTS[metric]
            for metric in FINANCIAL_METRIC_WEIGHTS
        ) / sum(FINANCIAL_METRIC_WEIGHTS.values())

        print(f"Normalized trend scores: {normalized_trend_scores}")
        print(f"Calculated weighted trend score: {weighted_trend_score:.2f}")
        return round(weighted_trend_score, 2), trend_results
    else:
        print("No trend data available for any metrics")
        return 5.0, {}  # Default to moderate risk if no trend data


def process_historical_financial_data(vendor_data):
    """
    Process and structure historical financial data for trend analysis.

    Args:
        vendor_data (dict): Vendor data containing financial metrics

    Returns:
        dict: Structured historical financial data by year
    """
    # Enhanced debugging
    print("Processing historical financial data for trend analysis")

    # Check if vendor_data contains historical financial data
    if 'historical_financial' not in vendor_data:
        print("No 'historical_financial' key found in vendor_data")
        return {}

    if not vendor_data['historical_financial']:
        print("'historical_financial' exists but is empty")
        return {}

    historical_data = vendor_data['historical_financial']
    print(f"Historical data type: {type(historical_data)}")

    # Detailed logging for dictionary content
    if isinstance(historical_data, dict):
        print(f"Historical data has {len(historical_data)} year entries")
        for year in sorted(historical_data.keys()):
            metrics = historical_data[year]
            if isinstance(metrics, dict):
                print(f"Year {year} has {len(metrics)} metrics: {', '.join(metrics.keys())}")
            else:
                print(f"Year {year} has unexpected data type: {type(metrics)}")
        return historical_data

    # If it's a DataFrame or list-like, convert it to our expected format
    structured_data = {}

    if isinstance(historical_data, pd.DataFrame):
        print(f"Processing DataFrame with {len(historical_data)} rows")
        # Convert DataFrame to dictionary
        for _, row in historical_data.iterrows():
            year = str(row.get('Year', ''))
            if year:
                structured_data[year] = {}
                for col, internal_key in EXCEL_TO_INTERNAL_KEYS.items():
                    if col in row and pd.notna(row[col]).all():
                        structured_data[year][internal_key] = float(row[col])

    elif isinstance(historical_data, list):
        print(f"Processing list with {len(historical_data)} items")
        # Assume list of dictionaries with 'Year' and other financial metrics
        for item in historical_data:
            if isinstance(item, dict) and 'Year' in item:
                year = str(item['Year'])
                structured_data[year] = {}

                for excel_key, internal_key in EXCEL_TO_INTERNAL_KEYS.items():
                    if excel_key in item and item[excel_key] is not None:
                        try:
                            structured_data[year][internal_key] = float(item[excel_key])
                        except (ValueError, TypeError):
                            print(f"Could not convert {item[excel_key]} to float for {excel_key} in year {year}")
                            pass
    else:
        print(f"Unsupported data type for historical_financial: {type(historical_data)}")

    print(f"Converted data structure has {len(structured_data)} years")
    return structured_data


def get_financial_stability_score(vendor_data):
    """
    Calculate and return the final financial stability score with historical trend analysis.

    Args:
        vendor_data (dict): Vendor data containing financial metrics

    Returns:
        float: The final weighted financial stability score
    """
    print("Starting financial stability score calculation")

    # 1. Calculate point-in-time score (current year)
    # Ensure vendor_data contains valid numerical values
    financial_metrics = {}

    for metric in FINANCIAL_METRIC_WEIGHTS:
        try:
            value = float(vendor_data.get(metric, 0))
            financial_metrics[metric] = value
            print(f"Found value for {metric}: {value}")
        except (ValueError, TypeError):
            # If conversion fails, use default value of 0
            financial_metrics[metric] = 0
            print(f"Could not convert {metric} value, using default of 0")

    # Calculate scores for each metric
    metric_scores = {
        metric: calculate_financial_metric_score(metric, value) 
        for metric, value in financial_metrics.items()
    }

    print(f"Current year metric scores: {metric_scores}")

    # Apply weightings and compute the current-year score
    weighted_current_score = sum(
        metric_scores[metric] * FINANCIAL_METRIC_WEIGHTS[metric] 
        for metric in metric_scores
    ) / sum(FINANCIAL_METRIC_WEIGHTS.values())

    print(f"Weighted current year score: {weighted_current_score:.2f}")

    # 2. Calculate historical trend score
    trend_score = 5.0  # Default moderate risk
    trend_details = {}

    # Check for pre-calculated trend analysis results
    if 'trend_analysis' in vendor_data and vendor_data['trend_analysis']:
        print("Using pre-calculated trend analysis")
        try:
            trend_results = vendor_data['trend_analysis']
            trend_scores = {}

            for metric, trend_info in trend_results.items():
                if metric in FINANCIAL_METRIC_WEIGHTS:
                    classification = trend_info.get('classification', 'stable')
                    # Use pre-calculated scores if available, otherwise use classification to look up score
                    if 'score' in trend_info:
                        trend_scores[metric] = trend_info['score']
                    else:
                        trend_scores[metric] = TREND_SCORES[metric].get(classification, 5)

            if trend_scores:
                # Use the same weights as point-in-time scoring for consistency
                weighted_trend_score = sum(
                    trend_scores.get(metric, 5) * FINANCIAL_METRIC_WEIGHTS.get(metric, 0)
                    for metric in FINANCIAL_METRIC_WEIGHTS
                ) / sum(FINANCIAL_METRIC_WEIGHTS.values())

                trend_score = round(weighted_trend_score, 2)
                trend_details = trend_results
        except Exception as e:
            print(f"Error processing pre-calculated trend data: {e}")
            # Fall back to processing historical data
            print("Falling back to processing historical data")
            historical_data = process_historical_financial_data(vendor_data)
            trend_score, trend_details = calculate_trend_score(historical_data)
    else:
        # Process historical data the traditional way
        print("Processing historical data from scratch")
        historical_data = process_historical_financial_data(vendor_data)
        trend_score, trend_details = calculate_trend_score(historical_data)

    # Store trend details in vendor_data for reporting
    vendor_data['trend_analysis'] = trend_details
    print(f"Calculated trend score: {trend_score:.2f}")

    # 3. Store additional information for visualizations
    vendor_data['historical_financial_structured'] = process_historical_financial_data(vendor_data)

    # 4. Calculate final combined score
    # 80% current year, 20% historical trend
    final_score = (weighted_current_score * 0.8) + (trend_score * 0.2)
    print(f"Final combined score (80% current, 20% trend): {final_score:.2f}")

    # Store component scores for reporting
    vendor_data['financial_point_in_time_score'] = round(weighted_current_score, 2)
    vendor_data['financial_trend_score'] = round(trend_score, 2)
    vendor_data['current_year_score'] = round(weighted_current_score, 2)  # Add for compatibility with test code

    return round(final_score, 2)


def interpret_financial_stability_risk_score(score):
    """
    Interpret the financial stability risk score.

    Args:
        score (float): The financial stability risk score

    Returns:
        tuple: (risk_category, interpretation_message)
    """
    # Aligned with VRRS thresholds for consistency
    if score >= 8.0:
        return "Severe Risk", "Potential bankruptcy or major financial distress. Avoid vendor."
    elif 6.5 <= score < 8.0:
        return "High Risk", "Poor financial health; high risk vendor. Consider alternative vendors. If selected, it will require closer monitoring."
    elif 4.5 <= score < 6.5:
        return "Moderate Risk", "Some financial concerns require monitoring."
    elif 2.5 <= score < 4.5:
        return "Low Risk", "Generally stable financial health with minor concerns."
    else:
        return "Very Low Risk", "Strong financial health, reliable vendor. Proceed with confidence."