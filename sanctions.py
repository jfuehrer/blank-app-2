"""
Sanctions scoring module for the Vendor Risk Reliability Score (VRRS) application.
Calculates risk scores based on sanctions data and violations.
"""
import re
import pandas as pd
import numpy as np

# Define violation keywords to search for
VIOLATION_KEYWORDS = [
    "violation", "violations", "violating", "violated"
]

# Thresholds for sanctions score (based on violation count)
SANCTIONS_THRESHOLDS = [
    (0, 0, 0),              # 0 violations = 0 points (no risk)
    (1, 3, 3),              # 1-3 violations = 3 points (low risk)
    (4, 10, 5),             # 4-10 violations = 5 points (medium risk)
    (11, 20, 7),            # 11-20 violations = 7 points (high risk)
    (21, float('inf'), 10)  # 21+ violations = 10 points (severe risk)
]

def extract_violation_count(text):
    """
    Extract the number of violations mentioned in the text.
    
    Args:
        text (str): The sanctions text to analyze
        
    Returns:
        int: The number of violations found, defaults to 1 if no specific number is found
    """
    if pd.isna(text) or not isinstance(text, str):
        return 0
    
    text = text.lower()
    
    # Check if any of the violation keywords are in the text
    if not any(keyword in text for keyword in VIOLATION_KEYWORDS):
        return 0
    
    # Look for patterns like "X violations" or "X violation(s)"
    number_patterns = [
        r'(\d+)\s+violation',  # Matches "40 violations" or "5 violation"
        r'settle\s+(\d+)\s+',  # Matches "settle 40 violations"
        r'alleged\s+(\d+)\s+'  # Matches "alleged 40 violations"
    ]
    
    for pattern in number_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Return the highest number found if multiple matches
            return max(int(match) for match in matches)
    
    # If there's mention of violations but no specific number, count as 1
    return 1

def score_with_thresholds(value, thresholds):
    """
    Generic function to score based on value and predefined thresholds.
    
    Args:
        value (int): The value to score
        thresholds (list): List of (lower_bound, upper_bound, score) tuples
        
    Returns:
        int: The assigned score based on thresholds
    """
    for lower, upper, score in thresholds:
        if lower <= value <= upper:
            return score
    return 0  # Default if no match

def get_sanctions_score(sanctions_data):
    """
    Calculate sanctions risk score based on violation counts.
    
    Args:
        sanctions_data (DataFrame or list): DataFrame with 'Sanctions' column or list of sanction texts
        
    Returns:
        tuple: (sanctions_score, violation_count, details)
    """
    total_violations = 0
    violations_per_entry = []
    
    # Handle different input types
    if isinstance(sanctions_data, pd.DataFrame):
        if 'Sanctions' in sanctions_data.columns:
            texts = sanctions_data['Sanctions'].tolist()
        else:
            return 0, 0, {"error": "No 'Sanctions' column found in DataFrame"}
    elif isinstance(sanctions_data, list):
        texts = sanctions_data
    elif isinstance(sanctions_data, dict) and 'sanctions' in sanctions_data:
        texts = sanctions_data['sanctions']
    else:
        return 0, 0, {"error": "Invalid sanctions data format"}
    
    # Process each sanction text
    for text in texts:
        if pd.isna(text) or not isinstance(text, str):
            continue
            
        violations = extract_violation_count(text)
        total_violations += violations
        
        if violations > 0:
            violations_per_entry.append({
                "text_sample": text[:100] + "..." if len(text) > 100 else text,
                "violations": violations
            })
    
    # Calculate score based on total violations
    sanctions_score = score_with_thresholds(total_violations, SANCTIONS_THRESHOLDS)
    
    # Normalize to scale of 0-10
    normalized_score = min(sanctions_score, 10)
    
    return normalized_score, total_violations, {
        "violation_details": violations_per_entry,
        "score_breakdown": f"Found {total_violations} total violations resulting in a score of {normalized_score}/10"
    }

def interpret_sanctions_score(score):
    """
    Interpret the sanctions risk score.
    
    Args:
        score (float): The sanctions risk score
        
    Returns:
        tuple: (risk_category, interpretation_message)
    """
    # Aligned with VRRS thresholds for consistency
    if score >= 80.0:  # 8.0 on normalized 0-10 scale
        return "Severe Risk", "The company has an extensive history of sanctions and regulatory violations, indicating severe compliance risks. Avoid."
    elif score >= 65.0:  # 6.5 on normalized 0-10 scale
        return "High Risk", "The company has a significant history of sanctions and regulatory violations, indicating substantial compliance risks."
    elif score >= 45.0:  # 4.5 on normalized 0-10 scale
        return "Moderate Risk", "The company has some history of sanctions or regulatory violations that need to be monitored."
    elif score >= 25.0:  # 2.5 on normalized 0-10 scale
        return "Low Risk", "The company has limited history of minor sanctions or regulatory issues."
    else:
        return "Very Low Risk", "The company has minimal or no history of sanctions or regulatory violations."
