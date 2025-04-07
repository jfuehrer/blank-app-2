"""
Foreign labor scoring module for the Vendor Risk Reliability Score (VRRS) application.
Calculates risk scores based on dependency on foreign labor and visa application patterns.
Now includes both point-in-time scoring and historical trend analysis.
"""

#need to figure out scipy issues row 10

import numpy as np
from scipy import stats

# Weights for current year vs trend analysis
CURRENT_YEAR_WEIGHT = 0.85  # 85% current year
TREND_WEIGHT = 0.15        # 15% trend

# Country risk multipliers
COUNTRY_RISK_MULTIPLIER = {
    'low_risk': 0.6,
    'moderate_risk': 0.8,
    'high_risk': 1.0
}

# Country risk categorization
RISK_CATEGORIZATION = {
    "low_risk": [
          "USA",
          "Canada",
          "Germany",
          "France",
          "United Kingdom",
          "Australia",
          "New Zealand",
          "Japan",
          "Sweden",
          "Norway",
          "Denmark",
          "Finland",
          "Netherlands",
          "Switzerland",
          "Belgium",
          "Austria",
          "Ireland",
          "Singapore",
          "South Korea"
        ],
        "moderate_risk": [
          "India",
          "Brazil",
          "Mexico",
          "South Africa",
          "Turkey",
          "Indonesia",
          "Thailand",
          "Philippines",
          "Vietnam",
          "Argentina",
          "Chile",
          "Colombia",
          "Malaysia",
          "Poland",
          "Czech Republic",
          "Hungary",
          "Saudi Arabia",
          "United Arab Emirates",
          "Qatar",
          "Egypt",
          "Peru",
          "Ukraine"
        ],
        "high_risk": [
          "Russia",
          "China",
          "Iran",
          "North Korea",
          "Venezuela",
          "Syria",
          "Afghanistan",
          "Pakistan",
          "Iraq",
          "Libya",
          "Somalia",
          "Sudan",
          "Yemen",
          "Zimbabwe",
          "Cuba",
          "Myanmar",
          "Eritrea",
          "Belarus",
          "Nicaragua",
          "Burundi"
        ]   
}

# Visa category scoring thresholds
VISA_CATEGORY_THRESHOLDS = {
    'certified': [
        (0, 10, 1), 
        (11, 20, 6), 
        (21, 50, 8), 
        (51, float('inf'), 10)
    ],
    'denied': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ],
    'withdrawn': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ],
    'certified_expired': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ],
    'unspecified': [
        (0, 10, 1), 
        (11, 20, 2), 
        (21, 50, 4), 
        (51, float('inf'), 6)
    ]
}

# Trend adjustment factors
TREND_ADJUSTMENT = {
    'favorable': 2,
    'neutral': 6,
    'unfavorable': 10
}

# Weights for combined scoring
CURRENT_YEAR_WEIGHT = 0.85
TREND_WEIGHT = 0.15

def score_with_thresholds(value, thresholds):
    """
    Score a value based on predefined thresholds.

    Args:
        value (float): The value to score
        thresholds (list): List of (lower_bound, upper_bound, score) tuples

    Returns:
        int: The assigned score based on thresholds
    """
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0

def get_country_risk_multiplier(country):
    """
    Get the risk multiplier based on the country.

    Args:
        country (str): The country name

    Returns:
        float: The risk multiplier for the country
    """
    for risk_level, countries in RISK_CATEGORIZATION.items():
        if country in countries:
            return COUNTRY_RISK_MULTIPLIER[risk_level]
    return COUNTRY_RISK_MULTIPLIER['moderate_risk']  # Default to moderate risk

def get_visa_category_score(vendor_data, count):
    """
    Calculate the score for a specific visa category based on counts.

    Args:
        category (str): Visa category (certified, denied, withdrawn, etc.)
        count (int): Number of visas in this category

    Returns:
        int: Score for this visa category
    
    # josh - below is from the score calculator need to work through this logic   
    """
    if 'h1b_data' in vendor_data or 'permanent_visa_data' in vendor_data:
        # Use the new trend analysis version when historical data is available
        foreign_labor_results = calculate_final_foreign_labor_score_with_trend(vendor_data)
        # Store the trend analysis details in the vendor_data
        vendor_data['foreign_labor_trend'] = {
            'current_year_score': foreign_labor_results['current_year_score'],
            'trend_score': foreign_labor_results['trend_score'],
            'trend_data': foreign_labor_results['trend_data'],
            'weights': foreign_labor_results['weights']
        }
    return score_with_thresholds(count, VISA_CATEGORY_THRESHOLDS.get(vendor_data, []))


def calculate_job_sensitivity_score(low, moderate, high):
    """Calculate the job sensitivity score based on the number of job types"""
    # Input validation
    low = max(0, int(low))
    moderate = max(0, int(moderate))
    high = max(0, int(high))

    total_jobs = low + moderate + high
    if total_jobs == 0:
        return 1  # no foreign labor means minimal job risk

    weighted_score = ((low * 1) + (moderate * 6) + (high * 10)) / total_jobs
    return weighted_score

def calculate_country_score_with_visa(country_data, visa_counts):
    """
    Calculate the foreign labor score for a specific country.

    Args:
        country_data (dict): Dictionary with country and job sensitivity counts
        visa_counts (dict): Dictionary with visa category counts

    Returns:
        float: The country-specific foreign labor score
    """
    country = country_data.get('country', 'Unknown')
    low_sensitivity_count = country_data.get('job_counts_low', 0)
    moderate_sensitivity_count = country_data.get('job_counts_moderate', 0)
    high_sensitivity_count = country_data.get('job_counts_high', 0)

    # Get the country risk multiplier
    risk_multiplier = get_country_risk_multiplier(country)

    # Calculate the job sensitivity score
    job_sensitivity_score = calculate_job_sensitivity_score(
        low_sensitivity_count, moderate_sensitivity_count, high_sensitivity_count
    )

    # Calculate base visa score and normalize categories
    total_visa_score = sum(
        get_visa_category_score(category, count) 
        for category, count in visa_counts.items()
    )
    normalized_visa_score = total_visa_score / max(len(visa_counts), 1)

    # Apply the country risk multiplier and weight to visa score
    adjusted_visa_score = normalized_visa_score * risk_multiplier

    # Combine job sensitivity score and adjusted visa score
    final_country_score = (job_sensitivity_score * 0.40) + (adjusted_visa_score * 0.60)
    final_country_score = min(max(final_country_score, 0), 10)  # Clamp between 0 and 10

    return final_country_score

def calculate_final_adjusted_foreign_labor_score(countries_data, visa_counts):
    """
    Calculate the final adjusted foreign labor score across multiple countries.

    Args:
        countries_data (list): List of country data dictionaries
        visa_counts (dict): Dictionary with visa counts

    Returns:
        float: Normalized foreign labor score
    """
    if not countries_data:
        return 0  # No foreign labor data

    country_scores = [
        calculate_country_score_with_visa(country_data, visa_counts) 
        for country_data in countries_data
    ]

    # Normalize the score by dividing by the number of countries
    total_score = sum(country_scores) 
    normalized_score = total_score / len(countries_data)

    return round(normalized_score, 2)

def calculate_final_foreign_labor_score(vendor_data):
    """
    Calculate the final foreign labor score for a vendor.

    Args:
        vendor_data (dict): Dictionary containing all relevant vendor information

    Returns:
        float: Final foreign labor risk score
    """
    # Get countries data, default to empty list if not present
    countries_data = vendor_data.get('countries_data', [])

    # Get visa counts, default to 0 if not present
    visa_counts = {
        'certified': vendor_data.get('visa_certified_count', 0),
        'denied': vendor_data.get('visa_denied_count', 0),
        'withdrawn': vendor_data.get('visa_withdrawn_count', 0),
        'certified_expired': vendor_data.get('visa_certified_expired_count', 0),
        'unspecified': vendor_data.get('visa_unspecified_count', 0)
    }

    # Calculate adjusted foreign labor score
    adjusted_foreign_labor_score = calculate_final_adjusted_foreign_labor_score(
        countries_data, visa_counts
    )

    # Return the final score
    return round(adjusted_foreign_labor_score, 2)

def analyze_visa_trend(years, values, metric):
    """
    Calculate the trend for a given visa metric using linear regression and classify as improving, stable, or declining.
    Enhanced with more sophisticated trend detection and relative change analysis.

    Args:
        years (list): List of years as numeric values
        values (list): List of metric values
        metric (str): The name of the metric being analyzed

    Returns:
        dict: Contains trend classification and slope information
    """
    if not years or not values or len(years) < 2 or len(values) < 2:
        return {
            'classification': 'stable',
            'score': 6,
            'slope': 0,
            'metric': metric,
            'significance': False,
            'direction': 'neutral',
            'color': 'orange',
            'symbol': '→'
        }

    # Ensure data is sorted by year
    paired_data = sorted(zip(years, values))
    sorted_years, sorted_values = zip(*paired_data)
    
    # Convert to numpy arrays
    x = np.array(sorted_years)
    y = np.array(sorted_values)

    # Calculate linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Calculate relative change for more accurate trend assessment
    if len(sorted_values) >= 2:
        first_value = sorted_values[0]
        last_value = sorted_values[-1]
        
        # Prevent division by zero
        if first_value != 0:
            relative_change = (last_value - first_value) / abs(first_value)
        else:
            relative_change = 0 if last_value == 0 else 1 if last_value > 0 else -1
    else:
        relative_change = 0
    
    # Determine statistical significance and practical significance
    statistical_sig = p_value < 0.05
    correlation_sig = abs(r_value) > 0.5
    
    # Magnitude significance thresholds should be adjusted by metric type
    # Higher threshold for common metrics, lower for more critical ones
    if metric in ['denied', 'withdrawn', 'denied_withdrawn']:
        magnitude_sig = abs(relative_change) > 0.20  # 20% change is significant for denials
    else:
        magnitude_sig = abs(relative_change) > 0.15  # 15% change for other metrics
    
    # A trend is significant if statistically significant or has both correlation and magnitude
    significant = statistical_sig or (correlation_sig and magnitude_sig)
    
    # For short time series, rely more on relative change than statistics
    if len(sorted_years) <= 3:
        significant = significant or abs(relative_change) > 0.25
    
    # Define thresholds for trend classification
    # More nuanced thresholds based on metric type and data characteristics
    if metric in ['denied', 'withdrawn', 'denied_withdrawn']:
        # For negative metrics, negative slope (decrease) is improvement
        if significant and slope < 0:
            classification = 'improving'
            score = 2
            direction = 'down'
            color = 'green'
            symbol = '↓'
        elif significant and slope > 0:
            classification = 'declining'
            score = 10
            direction = 'up'
            color = 'red'
            symbol = '↑'
        else:
            classification = 'stable'
            score = 6
            direction = 'neutral'
            color = 'orange'
            symbol = '→'
    elif metric in ['certified', 'certified_expired']:
        # For positive metrics, positive slope (increase) is improvement
        if significant and slope > 0:
            classification = 'improving'
            score = 2
            direction = 'up'
            color = 'green'
            symbol = '↑'
        elif significant and slope < 0:
            classification = 'declining'
            score = 10
            direction = 'down'
            color = 'red'
            symbol = '↓'
        else:
            classification = 'stable'
            score = 6
            direction = 'neutral'
            color = 'orange'
            symbol = '→'
    else:
        classification = 'stable'
        score = 6
        direction = 'neutral'
        color = 'orange'
        symbol = '→'

    return {
        'classification': classification,
        'score': score,
        'slope': slope,
        'intercept': intercept,
        'r_value': r_value,
        'p_value': p_value,
        'std_err': std_err,
        'r_squared': r_value**2,
        'statistical_sig': statistical_sig, 
        'correlation_sig': correlation_sig,
        'magnitude_sig': magnitude_sig,
        'relative_change': relative_change,
        'significance': significant,
        'metric': metric,
        'first_value': sorted_values[0],
        'last_value': sorted_values[-1],
        'direction': direction,
        'color': color,
        'symbol': symbol,
        'data_points': len(sorted_years)
    }

def process_historical_visa_data(visa_data):
    """
    Process historical visa data for trend analysis.

    Args:
        visa_data (dict): Dictionary containing visa data with keys:
            - h1b_data: List of dictionaries with Year, H1B Type, H1B Count
            - permanent_visa_data: List of dictionaries with Year, Permanent Visa Type, Permanent Visa Count

    Returns:
        dict: Structured historical visa data by year for trend analysis
    """
    # Initialize structure to hold historical data
    historical_data = {}

    # Process H1B visa data
    for entry in visa_data.get('h1b_data', []):
        # Check if entry is a dictionary (expected format)
        if isinstance(entry, dict):
            year = entry.get('Year')
            visa_type = entry.get('H1B Type', 'Unspecified')
            count = entry.get('H1B Count', 0)
        else:
            # Skip entries that aren't dictionaries
            print(f"Skipping non-dictionary entry in h1b_data: {entry}")
            continue

        if year not in historical_data:
            historical_data[year] = {
                'certified': 0,
                'denied': 0,
                'withdrawn': 0,
                'certified-withdrawn': 0,
                'certified-expired': 0,
                'unspecified': 0,
                'total': 0
            }

        # Map the visa type to our categories
        if visa_type == 'Certified':
            historical_data[year]['certified'] += count
        elif visa_type == 'Denied':
            historical_data[year]['denied'] += count
        elif visa_type == 'Withdrawn':
            historical_data[year]['withdrawn'] += count
        elif visa_type == 'Certified-Withdrawn':
            historical_data[year]['certified-withdrawn'] += count
        elif visa_type == 'Certified-Expired':
            historical_data[year]['certified_expired'] += count
        else:
            historical_data[year]['unspecified'] += count

        historical_data[year]['total'] += count

    # Process permanent visa data
    for entry in visa_data.get('permanent_visa_data', []):
        # Check if entry is a dictionary (expected format)
        if isinstance(entry, dict):
            year = entry.get('Year')
            visa_type = entry.get('Permanent Visa Type', 'Unspecified')
            count = entry.get('Permanent Visa Count', 0)
        else:
            # Skip entries that aren't dictionaries
            print(f"Skipping non-dictionary entry in permanent_visa_data: {entry}")
            continue

        if year not in historical_data:
            historical_data[year] = {
                'certified': 0,
                'denied': 0,
                'withdrawn': 0,
                'certified-withdrawn': 0,
                'certified-expired': 0,
                'unspecified': 0,
                'total': 0
            }

        # Map the visa type to our categories (similar to H1B)
        if visa_type == 'Certified':
            historical_data[year]['certified'] += count
        elif visa_type == 'Denied':
            historical_data[year]['denied'] += count
        elif visa_type == 'Withdrawn':
            historical_data[year]['withdrawn'] += count
        elif visa_type == 'Certified-Withdrawn':
            historical_data[year]['certified-withdrawn'] += count
        elif visa_type == 'Certified-Expired':
            historical_data[year]['certified_expired'] += count
        else:
            historical_data[year]['unspecified'] += count

        historical_data[year]['total'] += count

    return historical_data

def calculate_visa_trend_score(trend_data):
    """
    Calculate a score based on recent trends in visa applications.

    Args:
        trend_data (dict): Dictionary with trend classifications

    Returns:
        int: Trend adjustment score
    """
    # Check for high-risk trends in declining certified or increasing denied/withdrawn
    if trend_data.get('denied_withdrawn_trend') == 10 or trend_data.get('certified_trend') == 10:
        return TREND_ADJUSTMENT['unfavorable']
    # Check for low-risk trends in increasing certified or decreasing denied/withdrawn
    elif trend_data.get('certified_trend') == 2 and trend_data.get('denied_withdrawn_trend') == 2:
        return TREND_ADJUSTMENT['favorable']
    # Neutral case - stable trends
    elif trend_data.get('certified_trend') == 6 and trend_data.get('denied_withdrawn_trend') == 6:
        return TREND_ADJUSTMENT['neutral']
    # Default to moderate risk
    else:
        return TREND_ADJUSTMENT['neutral']

def calculate_trend_score(visa_data):
    """
    Calculate historical trend scores for visa metrics.

    Args:
        visa_data (dict): Dictionary containing visa data with historical information

    Returns:
        tuple: (trend_score, trend_details) - overall trend score and detailed breakdown
    """
    # Process the historical data
    historical_data = process_historical_visa_data(visa_data)

    # Extract years and ensure they're in chronological order
    years = sorted(historical_data.keys())

    # For trend analysis, focus on the most recent 5 years or all available if less
    if len(years) > 5:
        recent_years = years[-5:]
    else:
        recent_years = years

    # Extract metrics for trend analysis
    certified_values = [historical_data[year]['certified'] for year in recent_years]
    denied_values = [historical_data[year]['denied'] for year in recent_years]
    withdrawn_values = [historical_data[year]['withdrawn'] for year in recent_years]
    certified_withdrawn_values = [historical_data[year].get('certified-withdrawn', 0) for year in recent_years]
    certified_expired_values = [historical_data[year].get('certified_expired', 0) for year in recent_years] 
    unspecified_values = [historical_data[year]['unspecified'] for year in recent_years]

    # Combine denied and withdrawn for trend analysis
    denied_withdrawn_values = [denied + withdrawn + cert_with for denied, withdrawn, cert_with 
                              in zip(denied_values, withdrawn_values, certified_withdrawn_values)]

    # Analyze trends
    certified_trend = analyze_visa_trend(recent_years, certified_values, 'certified')
    # Use the previously calculated combined values
    denied_withdrawn_trend = analyze_visa_trend(recent_years, denied_withdrawn_values, 'denied_withdrawn')
    certified_expired_trend = analyze_visa_trend(recent_years, certified_expired_values, 'certified_expired')
    unspecified_trend = analyze_visa_trend(recent_years, unspecified_values, 'unspecified')
    

    # Compile trend data
    trend_data = {
        'certified_trend': certified_trend['score'],
        'denied_withdrawn_trend': denied_withdrawn_trend['score'],
        'trend_details': {
            'certified': certified_trend,
            'denied_withdrawn': denied_withdrawn_trend
        },
        'years_analyzed': len(recent_years)
    }

    # Calculate the final trend score
    trend_score = calculate_visa_trend_score(trend_data)

    return trend_score, trend_data

def calculate_final_foreign_labor_score_with_trend(vendor_data):
    """
    Calculate the final foreign labor score incorporating historical trend analysis.

    Args:
        vendor_data (dict): Dictionary containing all relevant vendor information
            including historical visa data

    Returns:
        dict: Comprehensive foreign labor risk assessment results
    """
    # Calculate current year score
    current_year_score = calculate_final_foreign_labor_score(vendor_data)

    # Set default trend score and data
    trend_score = 5.0  # Default moderate risk
    trend_data = {}
    
    # Check for pre-calculated trend analysis results
    if 'visa_trend_analysis' in vendor_data and vendor_data['visa_trend_analysis']:
        try:
            # Use pre-calculated trend analysis
            trend_results = vendor_data['visa_trend_analysis']
            visa_trends = {
                'h1b_certified': 5,  # Default scores
                'h1b_denied': 5,
                'h1b_withdrawn': 5,
                'perm_certified': 5,
                'perm_denied': 5
            }
            
            # Map the trend classifications to scores
            for metric, trend_info in trend_results.items():
                classification = trend_info.get('classification', 'stable')
                
                # Assign scores based on classification and metric type
                if classification == 'improving':
                    # For denied/withdrawn metrics, improvement means lower score (less risk)
                    if 'denied' in metric or 'withdrawn' in metric:
                        visa_trends[metric] = 2
                    else:  # For certified metrics, improvement means lower score (less risk)
                        visa_trends[metric] = 2
                elif classification == 'stable':
                    visa_trends[metric] = 5
                elif classification == 'declining':
                    # For denied/withdrawn metrics, decline means higher score (more risk)
                    if 'denied' in metric or 'withdrawn' in metric:
                        visa_trends[metric] = 8
                    else:  # For certified metrics, decline means higher score (more risk)
                        visa_trends[metric] = 8
            
            # Calculate weighted trend score - equal weights for simplicity
            if visa_trends:
                trend_score = sum(visa_trends.values()) / len(visa_trends)
                trend_data = trend_results
        except Exception as e:
            print(f"Error processing pre-calculated visa trend data: {e}")
            # Fall back to processing historical data
            visa_data = {
                'h1b_data': vendor_data.get('h1b_data', []),
                'permanent_visa_data': vendor_data.get('permanent_visa_data', [])
            }
            trend_score, trend_data = calculate_trend_score(visa_data)
    else:
        # Process historical data the traditional way
        visa_data = {
            'h1b_data': vendor_data.get('h1b_data', []),
            'permanent_visa_data': vendor_data.get('permanent_visa_data', [])
        }
        trend_score, trend_data = calculate_trend_score(visa_data)

    # Use the globally defined weights

    # Combine current year and trend scores
    final_score = (current_year_score * CURRENT_YEAR_WEIGHT) + (trend_score * TREND_WEIGHT)
    final_score = round(final_score, 2)

    # Create result dictionary
    result = {
        'foreign_labor_score': final_score,
        'current_year_score': current_year_score,
        'trend_score': trend_score,
        'trend_data': trend_data,
        'weights': {
            'current_year': CURRENT_YEAR_WEIGHT,
            'trend': TREND_WEIGHT
        }
    }

    # Add risk category interpretation
    risk_category, interpretation = interpret_foreign_labor_risk_score(final_score)
    result['risk_category'] = risk_category
    result['interpretation'] = interpretation

    return result

def interpret_foreign_labor_risk_score(score):
    """
    Interpret the foreign labor risk score.

    Args:
        score (float): The foreign labor risk score

    Returns:
        tuple: (risk_category, interpretation_message)
    """
    # Aligned with VRRS thresholds for consistency
    if score >= 8.0:
        return "Severe Risk", "Vendor exclusively relies on foreign labor for critical roles and exhibits extreme dependence on high-risk countries."
    elif 6.5 <= score < 8.0:
        return "High Risk", "Vendor heavily relies on foreign labor, high-risk roles, or exhibits increasing dependence on H1-B visas from high-risk countries."
    elif 4.5 <= score < 6.5:
        return "Moderate Risk", "Vendor uses significant foreign labor for moderately sensitive roles with some controls in place."
    elif 2.5 <= score < 4.5:
        return "Low Risk", "Vendor uses some foreign labor for low-risk roles with good controls in place."
    else:
        return "Very Low Risk", "Vendor has minimal reliance on foreign labor, low-risk roles, and favorable historical trend."