# Date Filter Troubleshooting Guide

## Quick Diagnostic Checklist

When the date filter isn't working as expected, follow this checklist:

### ✅ **Step 1: Verify Date Parsing**
```python
# Add this debug code to see actual date formats
for match in player_stats.get("match_data", [])[:5]:  # Check first 5 matches
    print(f"Date field: '{match.get('Date', 'NO DATE')}' (type: {type(match.get('Date'))})")
```

**Common Issues:**
- Date field doesn't exist → Check field name (might be 'date', 'Date', 'match_date')
- Wrong date format → Add new format to `date_formats` list
- Date is None/empty → Handle empty dates gracefully

### ✅ **Step 2: Check Filter Logic**
```python
# Verify the filter condition is correct
if match_date < start_date or match_date > end_date:  # ✅ CORRECT
    include_match = False

# NOT this (common mistake):
if match_date < start_date and match_date > end_date:  # ❌ WRONG - never true
    include_match = False
```

### ✅ **Step 3: Verify Deep Copy**
```python
# Use deep copy to avoid reference issues
import copy
filtered_player = copy.deepcopy(player_stats)  # ✅ CORRECT

# NOT this:
filtered_player = player_stats.copy()  # ❌ SHALLOW COPY - can cause issues
```

### ✅ **Step 4: Check Data Recalculation**
```python
# Verify all statistics are recalculated from filtered matches
total_minutes = sum(match.get("Minutes played", 0) for match in filtered_matches)
filtered_player["minutes"] = total_minutes  # Must update with new value
```

## Common Error Patterns

### 1. **"Date parsing error" Messages**

**Symptoms:**
- Console shows "Could not parse date" messages
- All matches are kept despite date filter

**Diagnosis:**
```python
# Check what date format you actually have
sample_dates = []
for player_data in player_data.values():
    for match in player_data.get("match_data", [])[:3]:
        if "Date" in match:
            sample_dates.append(match["Date"])
print("Sample dates:", sample_dates)
```

**Solutions:**
- Add your date format to the `date_formats` list
- Check for extra whitespace or special characters
- Verify date field name is correct

### 2. **"No players found" After Filtering**

**Symptoms:**
- Filter appears to work but returns 0 players
- All players disappear after applying filter

**Diagnosis:**
```python
# Check if any matches pass the filter
total_matches_before = 0
total_matches_after = 0
for player_name, player_stats in player_data.items():
    matches_before = len(player_stats.get("match_data", []))
    total_matches_before += matches_before
    
    # Apply your filter logic here and count matches_after
    print(f"{player_name}: {matches_before} → {matches_after} matches")
```

**Solutions:**
- Check date range is reasonable (not too narrow)
- Verify date parsing is working
- Check if date field exists in match data

### 3. **"Statistics Don't Update" Issue**

**Symptoms:**
- Filter appears to work but statistics remain unchanged
- Minutes/goals/assists show original values

**Diagnosis:**
```python
# Check if statistics are being recalculated
print(f"Original minutes: {original_player['minutes']}")
print(f"Filtered minutes: {filtered_player['minutes']}")
print(f"Calculated from matches: {sum(match.get('Minutes played', 0) for match in filtered_matches)}")
```

**Solutions:**
- Ensure all statistics are recalculated from `filtered_matches`
- Check field names match between calculation and data structure
- Verify deep copy is used

### 4. **"Filter Logic Not Working" Issue**

**Symptoms:**
- Dates outside range still appear
- Filter seems to have no effect

**Diagnosis:**
```python
# Add debug prints to see what's happening
for match in player_stats.get("match_data", []):
    if "Date" in match:
        match_date = parse_date_multiple_formats(match["Date"])
        include = not (match_date < start_date or match_date > end_date)
        print(f"Date: {match['Date']} → {match_date} → Include: {include}")
```

**Solutions:**
- Fix filter logic (use OR not AND)
- Check date comparison is working correctly
- Verify start_date and end_date are correct types

## Debug Code Snippets

### Quick Date Format Detector
```python
def detect_date_formats(player_data, max_samples=50):
    """Detect what date formats are used in your data"""
    date_samples = []
    for player_stats in player_data.values():
        for match in player_stats.get("match_data", []):
            if "Date" in match and len(date_samples) < max_samples:
                date_samples.append(match["Date"])
    
    print("Date samples found:")
    for i, date_sample in enumerate(set(date_samples)[:10]):
        print(f"  {i+1}. '{date_sample}' (type: {type(date_sample)})")
    
    return date_samples
```

### Filter Effectiveness Checker
```python
def check_filter_effectiveness(player_data, start_date, end_date):
    """Check how many matches are filtered out"""
    total_before = 0
    total_after = 0
    
    for player_name, player_stats in player_data.items():
        matches_before = len(player_stats.get("match_data", []))
        
        # Count matches that would pass filter
        matches_after = 0
        for match in player_stats.get("match_data", []):
            if "Date" in match:
                match_date = parse_date_multiple_formats(match["Date"])
                if match_date and start_date <= match_date <= end_date:
                    matches_after += 1
            else:
                matches_after += 1  # Keep matches without dates
        
        total_before += matches_before
        total_after += matches_after
        
        if matches_before != matches_after:
            print(f"{player_name}: {matches_before} → {matches_after} matches")
    
    print(f"Total: {total_before} → {total_after} matches ({total_after/total_before*100:.1f}% kept)")
```

### Statistics Consistency Checker
```python
def check_statistics_consistency(filtered_player_data):
    """Verify that stored statistics match calculated statistics"""
    for player_name, player_stats in filtered_player_data.items():
        stored_minutes = player_stats.get("minutes", 0)
        calculated_minutes = sum(match.get("Minutes played", 0) for match in player_stats.get("match_data", []))
        
        if stored_minutes != calculated_minutes:
            print(f"❌ {player_name}: Stored={stored_minutes}, Calculated={calculated_minutes}")
        else:
            print(f"✅ {player_name}: Minutes consistent ({stored_minutes})")
```

## Performance Optimization

### For Large Datasets

1. **Cache Parsed Dates**
```python
date_cache = {}
def parse_date_cached(date_str):
    if date_str not in date_cache:
        date_cache[date_str] = parse_date_multiple_formats(date_str)
    return date_cache[date_str]
```

2. **Use Vectorized Operations**
```python
# For pandas DataFrames
df['parsed_date'] = pd.to_datetime(df['Date'], errors='coerce')
filtered_df = df[(df['parsed_date'] >= start_date) & (df['parsed_date'] <= end_date)]
```

3. **Implement Progress Indicators**
```python
import streamlit as st

progress_bar = st.progress(0)
total_players = len(player_data)

for i, (player_name, player_stats) in enumerate(player_data.items()):
    # Filter logic here
    progress_bar.progress((i + 1) / total_players)
```

## Testing Your Implementation

### Unit Test Template
```python
def test_date_filter():
    # Test data
    test_data = {
        "Test Player": {
            "match_data": [
                {"Date": "2024-08-15", "Minutes played": 90},
                {"Date": "2024-09-15", "Minutes played": 85},
                {"Date": "2025-01-15", "Minutes played": 80},
            ]
        }
    }
    
    # Apply filter
    start_date = datetime.date(2024, 9, 1)
    end_date = datetime.date(2024, 12, 31)
    filtered_data = apply_date_filter(test_data, start_date, end_date)
    
    # Verify results
    assert "Test Player" in filtered_data
    assert len(filtered_data["Test Player"]["match_data"]) == 1
    assert filtered_data["Test Player"]["minutes"] == 85
    
    print("✅ Date filter test passed!")
```

### Integration Test
```python
def test_full_workflow():
    # Test with real data sample
    sample_data = get_sample_player_data()  # Your data loading function
    
    # Apply filter
    start_date = datetime.date(2024, 8, 1)
    end_date = datetime.date(2024, 12, 31)
    filtered_data = apply_date_filter(sample_data, start_date, end_date)
    
    # Verify no data corruption
    for player_name, player_stats in filtered_data.items():
        assert "match_data" in player_stats
        assert "minutes" in player_stats
        assert "matches" in player_stats
        
        # Verify consistency
        calculated_minutes = sum(match.get("Minutes played", 0) for match in player_stats["match_data"])
        assert player_stats["minutes"] == calculated_minutes
    
    print("✅ Full workflow test passed!")
```

## When to Contact Support

If you've tried all the above steps and the filter still isn't working:

1. **Gather Debug Information:**
   - Sample of your date formats
   - Error messages from console
   - Expected vs actual behavior
   - Code snippets you're using

2. **Create Minimal Reproduction:**
   - Simplify to smallest possible example
   - Use sample data that demonstrates the issue
   - Include complete error messages

3. **Document Your Environment:**
   - Python version
   - Streamlit version
   - Data structure format
   - Operating system

The most common issues are date format mismatches and incorrect filter logic - double-check these first!
