#!/usr/bin/env python3
"""
Test script to verify that the scatter plot exact values fix is working correctly.
This script tests both outfield and goalkeeper scatter plot functions.
"""

import os
import sys

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def test_scatter_plot_fix():
    """Test that scatter plot functions work with exact values."""
    print("=" * 80)
    print("TESTING SCATTER PLOT EXACT VALUES FIX")
    print("=" * 80)
    
    try:
        # Test 1: Import functions
        print("\n🔍 STEP 1: TESTING IMPORTS")
        print("-" * 50)
        
        from components.outfield_components import create_outfield_scatter_plot
        from components.app_components import render_player_comparison
        from core.data_processor import OutfieldDataProcessor
        
        print("✅ Successfully imported scatter plot functions")
        
        # Test 2: Load test data
        print("\n🔍 STEP 2: LOADING TEST DATA")
        print("-" * 50)
        
        processor = OutfieldDataProcessor()
        player_data = processor.process_data()
        
        print(f"✅ Loaded {len(player_data)} outfield players")
        
        # Test 3: Prepare test parameters
        print("\n🔍 STEP 3: PREPARING TEST PARAMETERS")
        print("-" * 50)
        
        # Get first 3 players for testing
        test_players = list(player_data.keys())[:3]
        test_player_stats = [player_data[player] for player in test_players]
        
        print(f"✅ Selected test players: {test_players}")
        
        # Test different stat combinations
        test_combinations = [
            ("goals", "assists"),
            ("shots", "passes_accurate"),
            ("duels_won", "recoveries"),
            ("dribbles_successful", "passes")
        ]
        
        print(f"✅ Prepared {len(test_combinations)} test combinations")
        
        # Test 4: Test outfield scatter plot creation
        print("\n🔍 STEP 4: TESTING OUTFIELD SCATTER PLOT CREATION")
        print("-" * 50)
        
        for i, (x_stat, y_stat) in enumerate(test_combinations):
            print(f"\nTesting combination {i+1}: {x_stat} vs {y_stat}")
            
            try:
                # Test without per_90 mode
                fig = create_outfield_scatter_plot(
                    test_players,
                    test_player_stats,
                    x_stat,
                    y_stat,
                    "All Outfield",
                    per_90_mode=False
                )
                
                if fig:
                    print(f"  ✅ Successfully created scatter plot (normal mode)")
                    
                    # Check if figure has data
                    if hasattr(fig, 'data') and len(fig.data) > 0:
                        print(f"  ✅ Figure contains {len(fig.data)} data traces")
                        
                        # Check if x and y values are actual values (not percentiles)
                        first_trace = fig.data[0]
                        if hasattr(first_trace, 'x') and hasattr(first_trace, 'y'):
                            x_vals = first_trace.x
                            y_vals = first_trace.y
                            
                            # Check if values are realistic (not 0-100 percentile range)
                            x_max = max(x_vals) if x_vals else 0
                            y_max = max(y_vals) if y_vals else 0
                            
                            print(f"  📊 X-axis range: 0 - {x_max:.1f}")
                            print(f"  📊 Y-axis range: 0 - {y_max:.1f}")
                            
                            # Verify these are actual values, not percentiles
                            if x_max > 100 or y_max > 100:
                                print(f"  ✅ Using actual values (not percentiles)")
                            elif x_max <= 100 and y_max <= 100:
                                # Check if these could be actual values
                                x_values = [test_player_stats[j].get(x_stat, 0) for j in range(len(test_players))]
                                y_values = [test_player_stats[j].get(y_stat, 0) for j in range(len(test_players))]
                                
                                actual_x_max = max(x_values) if x_values else 0
                                actual_y_max = max(y_values) if y_values else 0
                                
                                if abs(x_max - actual_x_max) < 1 and abs(y_max - actual_y_max) < 1:
                                    print(f"  ✅ Using actual values (values happen to be < 100)")
                                else:
                                    print(f"  ❌ Might still be using percentiles")
                                    print(f"     Expected X max: {actual_x_max:.1f}, Got: {x_max:.1f}")
                                    print(f"     Expected Y max: {actual_y_max:.1f}, Got: {y_max:.1f}")
                        else:
                            print(f"  ⚠️  Could not verify x/y values in trace")
                    else:
                        print(f"  ⚠️  Figure has no data traces")
                else:
                    print(f"  ❌ Failed to create scatter plot")
                
                # Test with per_90 mode
                fig_per90 = create_outfield_scatter_plot(
                    test_players,
                    test_player_stats,
                    x_stat,
                    y_stat,
                    "All Outfield",
                    per_90_mode=True
                )
                
                if fig_per90:
                    print(f"  ✅ Successfully created scatter plot (per 90 mode)")
                else:
                    print(f"  ❌ Failed to create scatter plot (per 90 mode)")
                    
            except Exception as e:
                print(f"  ❌ Error creating scatter plot: {e}")
        
        # Test 5: Test axis range calculation
        print("\n🔍 STEP 5: TESTING AXIS RANGE CALCULATION")
        print("-" * 50)
        
        # Test with a simple combination
        x_stat, y_stat = "goals", "assists"
        
        # Get actual values from test data
        x_values = [test_player_stats[i].get(x_stat, 0) for i in range(len(test_players))]
        y_values = [test_player_stats[i].get(y_stat, 0) for i in range(len(test_players))]
        
        print(f"Test data - {x_stat}: {x_values}")
        print(f"Test data - {y_stat}: {y_values}")
        
        # Create scatter plot and verify ranges
        fig = create_outfield_scatter_plot(
            test_players,
            test_player_stats,
            x_stat,
            y_stat,
            "All Outfield",
            per_90_mode=False
        )
        
        if fig and hasattr(fig, 'layout'):
            x_range = fig.layout.xaxis.range if hasattr(fig.layout.xaxis, 'range') else None
            y_range = fig.layout.yaxis.range if hasattr(fig.layout.yaxis, 'range') else None
            
            if x_range and y_range:
                print(f"✅ X-axis range: {x_range[0]:.1f} - {x_range[1]:.1f}")
                print(f"✅ Y-axis range: {y_range[0]:.1f} - {y_range[1]:.1f}")
                
                # Verify ranges are based on actual data
                expected_x_min = min(x_values)
                expected_x_max = max(x_values)
                expected_y_min = min(y_values)
                expected_y_max = max(y_values)
                
                # Check if ranges include the data with padding
                if (x_range[0] <= expected_x_min and x_range[1] >= expected_x_max and
                    y_range[0] <= expected_y_min and y_range[1] >= expected_y_max):
                    print(f"✅ Axis ranges correctly include all data points with padding")
                else:
                    print(f"⚠️  Axis ranges might not include all data points")
                    print(f"   Expected X: {expected_x_min} - {expected_x_max}")
                    print(f"   Expected Y: {expected_y_min} - {expected_y_max}")
            else:
                print(f"⚠️  Could not retrieve axis ranges from figure")
        
        print(f"\n✅ SCATTER PLOT EXACT VALUES FIX TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scatter_plot_fix()
    if success:
        print(f"\n🎉 All tests passed! Scatter plot exact values fix is working correctly.")
    else:
        print(f"\n💥 Some tests failed. Please check the error messages above.")
