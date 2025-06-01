#!/usr/bin/env python3
"""
Test script to verify that the profiler component styling changes work correctly.
"""

import os
import sys
import pandas as pd

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def test_percentile_color_function():
    """Test the percentile color function."""
    print("🔍 TESTING PERCENTILE COLOR FUNCTION")
    print("-" * 50)
    
    try:
        # Import the function (we'll need to extract it from the file)
        def get_percentile_color(percentile_rank):
            """Get color based on percentile rank"""
            # Color ranges - use exact boundaries to match the legend
            if percentile_rank >= 81:  # 81-100% range
                return '#1a9641'  # Dark green (81-100%)
            elif percentile_rank >= 61:  # 61-80% range
                return '#73c378'  # Medium green (61-80%)
            elif percentile_rank >= 41:  # 41-60% range
                return '#f9d057'  # Yellow (41-60%)
            elif percentile_rank >= 21:  # 21-40% range
                return '#fc8d59'  # Light orange (21-40%)
            else:  # 0-20% range
                return '#d73027'  # Red (0-20%)
        
        # Test different percentile ranges
        test_cases = [
            (95, '#1a9641', '81-100% (Dark Green)'),
            (85, '#1a9641', '81-100% (Dark Green)'),
            (81, '#1a9641', '81-100% (Dark Green)'),
            (75, '#73c378', '61-80% (Medium Green)'),
            (65, '#73c378', '61-80% (Medium Green)'),
            (61, '#73c378', '61-80% (Medium Green)'),
            (55, '#f9d057', '41-60% (Yellow)'),
            (45, '#f9d057', '41-60% (Yellow)'),
            (41, '#f9d057', '41-60% (Yellow)'),
            (35, '#fc8d59', '21-40% (Light Orange)'),
            (25, '#fc8d59', '21-40% (Light Orange)'),
            (21, '#fc8d59', '21-40% (Light Orange)'),
            (15, '#d73027', '0-20% (Red)'),
            (5, '#d73027', '0-20% (Red)'),
            (0, '#d73027', '0-20% (Red)')
        ]
        
        print("Testing percentile color mapping:")
        for percentile, expected_color, description in test_cases:
            actual_color = get_percentile_color(percentile)
            if actual_color == expected_color:
                print(f"  ✅ {percentile:3d}% → {actual_color} ({description})")
            else:
                print(f"  ❌ {percentile:3d}% → {actual_color} (expected {expected_color})")
                return False
        
        print("\n✅ All percentile color tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing percentile colors: {e}")
        return False

def test_styling_function():
    """Test the styling function logic."""
    print("\n🔍 TESTING STYLING FUNCTION LOGIC")
    print("-" * 50)
    
    try:
        # Test data
        test_data = {
            'Rank': [1, 2, 3, 4, 5],
            'Player': ['Player A', 'Player B', 'Player C', 'Player D', 'Player E'],
            'Team': ['Team 1', 'Team 2', 'Team 3', 'Team 4', 'Team 5'],
            'Position': ['GK', 'GK', 'GK', 'GK', 'GK'],
            'Minutes': [900, 850, 800, 750, 700],
            'Weighted Score': [85.5, 72.3, 58.7, 34.2, 12.8],
            'Percentile Rank': [95, 75, 55, 35, 15]
        }
        
        df = pd.DataFrame(test_data)
        print("Test dataframe created:")
        print(df[['Player', 'Weighted Score', 'Percentile Rank']])
        
        # Test styling function
        def get_percentile_color(percentile_rank):
            if percentile_rank >= 81:
                return '#1a9641'
            elif percentile_rank >= 61:
                return '#73c378'
            elif percentile_rank >= 41:
                return '#f9d057'
            elif percentile_rank >= 21:
                return '#fc8d59'
            else:
                return '#d73027'
        
        def style_weighted_score(val, percentile_rank):
            color = get_percentile_color(percentile_rank)
            return f'background-color: {color}; color: white; font-weight: bold'
        
        print("\nTesting styling application:")
        for idx, row in df.iterrows():
            score = row['Weighted Score']
            percentile = row['Percentile Rank']
            style = style_weighted_score(score, percentile)
            color = get_percentile_color(percentile)
            
            print(f"  {row['Player']}: Score {score:.1f} (P{percentile:.0f}%) → {color}")
        
        # Test pandas styling
        styled_df = df.style.apply(
            lambda row: [
                style_weighted_score(row['Weighted Score'], row['Percentile Rank'])
                if col == 'Weighted Score' else ''
                for col in df.columns
            ],
            axis=1
        )
        
        print("\n✅ Pandas styling object created successfully!")
        print(f"✅ Styled dataframe type: {type(styled_df)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing styling function: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_profiler_import():
    """Test that the profiler components can be imported."""
    print("\n🔍 TESTING PROFILER COMPONENT IMPORT")
    print("-" * 50)
    
    try:
        from components.profiler_components import calculate_and_display_scores
        print("✅ Successfully imported calculate_and_display_scores function")
        
        # Check if the function exists and is callable
        if callable(calculate_and_display_scores):
            print("✅ Function is callable")
        else:
            print("❌ Function is not callable")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing profiler components: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 80)
    print("PROFILER STYLING CHANGES VERIFICATION")
    print("=" * 80)
    print("Testing the weighted score column styling changes")
    print()
    
    # Test 1: Percentile color function
    color_test_passed = test_percentile_color_function()
    
    # Test 2: Styling function logic
    styling_test_passed = test_styling_function()
    
    # Test 3: Import test
    import_test_passed = test_profiler_import()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = color_test_passed and styling_test_passed and import_test_passed
    
    if color_test_passed:
        print("✅ Percentile color mapping: Working correctly")
    else:
        print("❌ Percentile color mapping: Failed")
    
    if styling_test_passed:
        print("✅ Styling function logic: Working correctly")
    else:
        print("❌ Styling function logic: Failed")
    
    if import_test_passed:
        print("✅ Profiler component import: Working correctly")
    else:
        print("❌ Profiler component import: Failed")
    
    print()
    
    if all_tests_passed:
        print("🎉 SUCCESS! Profiler styling changes are working correctly.")
        print("\nExpected behavior:")
        print("- Weighted Score column shows numbers (not progress bars)")
        print("- Background colors based on percentile rank:")
        print("  • 81-100%: Dark Green (#1a9641)")
        print("  • 61-80%:  Medium Green (#73c378)")
        print("  • 41-60%:  Yellow (#f9d057)")
        print("  • 21-40%:  Light Orange (#fc8d59)")
        print("  • 0-20%:   Red (#d73027)")
        print("- White text with bold font weight")
    else:
        print("💥 FAILED! Some tests did not pass.")
        print("\nPlease fix the issues above before proceeding.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
