# Local Date Filter Implementation Guide

## Overview

This document provides a comprehensive guide on implementing a local date filter in Streamlit applications for filtering player data by date ranges. The implementation includes robust date parsing, data recalculation, and user interface components.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Architecture](#solution-architecture)
3. [Implementation Steps](#implementation-steps)
4. [Code Examples](#code-examples)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Problem Statement

### Issues with Global Date Filters
- Global date filters may not work consistently across different components
- Session state conflicts can cause filtering to fail
- Data caching issues prevent proper filter application
- Need for component-specific date filtering for better control

### Requirements
- Filter player match data by custom date ranges
- Recalculate all statistics based on filtered matches
- Provide user feedback and debugging capabilities
- Handle multiple date formats gracefully
- Maintain data integrity during filtering

## Solution Architecture

### Components
1. **UI Components**: Date input controls and checkboxes
2. **Date Parser**: Multi-format date parsing function
3. **Data Filter**: Core filtering logic with deep copy
4. **Statistics Recalculator**: Aggregate statistics from filtered matches
5. **Debug Interface**: Verification and troubleshooting tools

### Data Flow
```
Original Data → Date Filter → Filtered Matches → Recalculated Stats → UI Display
```

## Implementation Steps

### Step 1: Add Required Imports

```python
import streamlit as st
import pandas as pd
import datetime
import copy
```

### Step 2: Create Date Filter UI

```python
# Date filter section
st.subheader("📅 Date Filter")
use_date_filter = st.checkbox("Enable Date Filter", value=False, help="Filter matches by date range")

if use_date_filter:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.date(2024, 8, 1),
            min_value=datetime.date(2020, 1, 1),
            max_value=datetime.date(2030, 12, 31),
            help="Start date for filtering matches"
        )
    with col2:
        end_date = st.date_input(
            "End Date", 
            value=datetime.date(2025, 6, 30),
            min_value=datetime.date(2020, 1, 1),
            max_value=datetime.date(2030, 12, 31),
            help="End date for filtering matches"
        )
```

### Step 3: Apply Date Filter

```python
# Apply date filter to player data
if start_date and end_date:
    st.info(f"📊 Filtering data from {start_date} to {end_date}")
    original_player_count = len(player_data)
    player_data = apply_date_filter(player_data, start_date, end_date)
    
    # Update players list after filtering
    players = list(player_data.keys())
    players.sort()
    
    # Show filtering results
    filtered_player_count = len(players)
    st.success(f"✅ Date filter applied: {filtered_player_count} players found (was {original_player_count})")
    
    if not players:
        st.warning("No players found with matches in the selected date range.")
        return
```

### Step 4: Implement Core Filter Function

```python
def apply_date_filter(player_data, start_date, end_date):
    """
    Apply date filter to player data and recalculate statistics.
    
    Args:
        player_data: Dictionary of player data
        start_date: Start date for filtering
        end_date: End date for filtering
    
    Returns:
        Filtered player data with recalculated statistics
    """
    filtered_data = {}
    
    for player_name, player_stats in player_data.items():
        # Create a deep copy to avoid reference issues
        filtered_player = copy.deepcopy(player_stats)
        
        # Filter match data
        filtered_matches = []
        for match in player_stats.get("match_data", []):
            include_match = True
            
            # Apply date filter with robust parsing
            if "Date" in match:
                try:
                    date_str = str(match["Date"]).strip()
                    match_date = parse_date_multiple_formats(date_str)
                    
                    if match_date:
                        if match_date < start_date or match_date > end_date:
                            include_match = False
                    else:
                        print(f"Could not parse date '{date_str}' for player {player_name}")
                        
                except Exception as e:
                    print(f"Date parsing error for player {player_name}: {match.get('Date', 'No Date')} - Error: {e}")
            
            if include_match:
                filtered_matches.append(match)
        
        # Only include player if they have matches after filtering
        if filtered_matches:
            # Update match data
            filtered_player["match_data"] = filtered_matches
            
            # Recalculate statistics
            recalculate_player_statistics(filtered_player, filtered_matches, player_stats)
            filtered_data[player_name] = filtered_player
    
    return filtered_data
```

## Code Examples

### Multi-Format Date Parser

```python
def parse_date_multiple_formats(date_str):
    """
    Parse date string using multiple common formats.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime.date object or None if parsing fails
    """
    date_formats = [
        "%Y-%m-%d",           # 2024-08-15
        "%d/%m/%Y",           # 15/08/2024
        "%m/%d/%Y",           # 08/15/2024
        "%d-%m-%Y",           # 15-08-2024
        "%Y/%m/%d",           # 2024/08/15
        "%d.%m.%Y",           # 15.08.2024
        "%Y-%m-%d %H:%M:%S",  # 2024-08-15 14:30:00
        "%d/%m/%Y %H:%M:%S",  # 15/08/2024 14:30:00
        "%m/%d/%Y %H:%M:%S",  # 08/15/2024 14:30:00
        "%Y-%m-%d %H:%M",     # 2024-08-15 14:30
        "%d/%m/%Y %H:%M",     # 15/08/2024 14:30
    ]
    
    for date_format in date_formats:
        try:
            return datetime.datetime.strptime(date_str, date_format).date()
        except (ValueError, TypeError):
            continue
    
    return None
```

### Statistics Recalculation

```python
def recalculate_player_statistics(filtered_player, filtered_matches, original_stats):
    """
    Recalculate player statistics from filtered matches.
    
    Args:
        filtered_player: Player data dictionary to update
        filtered_matches: List of filtered match data
        original_stats: Original player statistics for reference
    """
    total_matches = len(filtered_matches)
    total_minutes = sum(match.get("Minutes played", 0) for match in filtered_matches)
    
    # Update basic info
    filtered_player["matches"] = total_matches
    filtered_player["minutes"] = total_minutes
    
    if "saves" in original_stats:  # Goalkeeper
        recalculate_goalkeeper_stats(filtered_player, filtered_matches)
    else:  # Outfield player
        recalculate_outfield_stats(filtered_player, filtered_matches)
```

### Debug Interface

```python
# Debug information
if st.checkbox("🔍 Show Date Filter Debug Info", value=False):
    st.markdown("### 🔍 Date Filter Debug Information")
    
    # Show overall filtering results
    st.markdown(f"**Original player count**: {original_player_count}")
    st.markdown(f"**Filtered player count**: {filtered_player_count}")
    st.markdown(f"**Date range**: {start_date} to {end_date}")
    
    # Check specific player
    if "David da Silva" in player_data:
        david_stats = player_data["David da Silva"]
        st.markdown("**🎯 David da Silva Debug Info:**")
        st.markdown(f"**Filtered Minutes**: {david_stats.get('minutes', 'N/A')}")
        st.markdown(f"**Filtered Matches**: {david_stats.get('matches', 'N/A')}")
        
        # Verify data consistency
        match_data = david_stats.get('match_data', [])
        total_minutes_from_matches = sum(match.get('Minutes played', 0) for match in match_data)
        
        if david_stats.get('minutes', 0) == total_minutes_from_matches:
            st.success("✅ Minutes calculation is consistent!")
        else:
            st.error(f"❌ Minutes mismatch! Stored: {david_stats.get('minutes', 0)}, Calculated: {total_minutes_from_matches}")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Date Parsing Failures
**Problem**: Dates not being parsed correctly
**Solution**: 
- Check actual date format in your data
- Add new format to `date_formats` list
- Use debug prints to see failing date strings

#### 2. Data Not Filtering
**Problem**: All matches still appear after filtering
**Solution**:
- Verify date filter logic (use OR not AND)
- Check if date field exists in match data
- Ensure deep copy is used to avoid reference issues

#### 3. Statistics Mismatch
**Problem**: Calculated statistics don't match filtered data
**Solution**:
- Verify all statistics are recalculated from filtered matches
- Check field names match between calculation and data
- Use debug interface to verify consistency

#### 4. Performance Issues
**Problem**: Slow filtering with large datasets
**Solution**:
- Implement caching for parsed dates
- Use vectorized operations where possible
- Consider pagination for large result sets

### Debug Checklist

- [ ] Date parsing working for all formats
- [ ] Filter logic correctly excludes dates outside range
- [ ] Deep copy prevents reference issues
- [ ] All statistics recalculated from filtered matches
- [ ] UI shows correct filtered counts
- [ ] Debug information displays correctly

## Best Practices

### 1. Error Handling
- Always use try-catch blocks for date parsing
- Provide fallback behavior for unparseable dates
- Log errors for debugging purposes

### 2. Data Integrity
- Use deep copy to avoid modifying original data
- Verify calculated statistics match filtered data
- Implement consistency checks

### 3. User Experience
- Provide clear feedback on filtering results
- Show progress indicators for large datasets
- Include debug options for troubleshooting

### 4. Performance
- Cache parsed dates when possible
- Use efficient data structures
- Implement lazy loading for large datasets

### 5. Maintainability
- Separate concerns (UI, filtering, calculation)
- Use descriptive function and variable names
- Document complex logic thoroughly

## Conclusion

The local date filter implementation provides a robust solution for filtering player data by date ranges. By following this guide, you can implement reliable date filtering that handles multiple date formats, maintains data integrity, and provides excellent user experience with debugging capabilities.

The key to success is proper error handling, data validation, and comprehensive testing with various date formats and edge cases.
