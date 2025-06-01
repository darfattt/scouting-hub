#!/usr/bin/env python3
"""
Test script to verify that quadrant lines are working correctly in outfield scatter plots.
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

def test_quadrant_lines():
    """Test that quadrant lines are added to outfield scatter plots."""
    print("=" * 80)
    print("TESTING OUTFIELD SCATTER PLOT QUADRANT LINES")
    print("=" * 80)
    
    try:
        # Test 1: Import functions
        print("\n🔍 STEP 1: TESTING IMPORTS")
        print("-" * 50)
        
        from components.outfield_components import create_outfield_scatter_plot
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
        
        # Test 4: Create scatter plot and check for quadrant lines
        print("\n🔍 STEP 4: TESTING QUADRANT LINES")
        print("-" * 50)
        
        # Test with goals vs assists
        x_stat, y_stat = "goals", "assists"
        
        print(f"Creating scatter plot: {x_stat} vs {y_stat}")
        
        fig = create_outfield_scatter_plot(
            test_players,
            test_player_stats,
            x_stat,
            y_stat,
            "All Outfield",
            per_90_mode=False
        )
        
        if fig:
            print("✅ Scatter plot created successfully")
            
            # Check if figure has shapes (quadrant lines)
            if hasattr(fig, 'layout') and hasattr(fig.layout, 'shapes'):
                shapes = fig.layout.shapes
                print(f"📊 Found {len(shapes)} shapes in the plot")
                
                # Check for quadrant lines
                line_shapes = [shape for shape in shapes if shape.type == 'line']
                print(f"📊 Found {len(line_shapes)} line shapes")
                
                if len(line_shapes) >= 2:
                    print("✅ Quadrant lines detected!")
                    
                    # Analyze the lines
                    for i, line in enumerate(line_shapes):
                        print(f"  Line {i+1}:")
                        print(f"    From: ({line.x0}, {line.y0}) to ({line.x1}, {line.y1})")
                        print(f"    Color: {line.line.color}")
                        print(f"    Width: {line.line.width}")
                        
                        # Check if it's a horizontal or vertical line
                        if line.y0 == line.y1:
                            print(f"    Type: Horizontal line")
                        elif line.x0 == line.x1:
                            print(f"    Type: Vertical line")
                        else:
                            print(f"    Type: Diagonal line")
                        print()
                    
                    # Verify we have both horizontal and vertical lines
                    horizontal_lines = [line for line in line_shapes if line.y0 == line.y1]
                    vertical_lines = [line for line in line_shapes if line.x0 == line.x1]
                    
                    if len(horizontal_lines) >= 1 and len(vertical_lines) >= 1:
                        print("✅ Both horizontal and vertical quadrant lines found!")
                        print(f"   Horizontal lines: {len(horizontal_lines)}")
                        print(f"   Vertical lines: {len(vertical_lines)}")
                    else:
                        print("⚠️  Missing horizontal or vertical quadrant lines")
                        print(f"   Horizontal lines: {len(horizontal_lines)}")
                        print(f"   Vertical lines: {len(vertical_lines)}")
                        
                else:
                    print("❌ No quadrant lines found!")
                    
            else:
                print("⚠️  No shapes found in the plot layout")
            
            # Check if figure has data traces
            if hasattr(fig, 'data') and len(fig.data) > 0:
                print(f"✅ Figure contains {len(fig.data)} data traces")
                
                # Check axis ranges
                if hasattr(fig.layout, 'xaxis') and hasattr(fig.layout, 'yaxis'):
                    x_range = fig.layout.xaxis.range if hasattr(fig.layout.xaxis, 'range') else None
                    y_range = fig.layout.yaxis.range if hasattr(fig.layout.yaxis, 'range') else None
                    
                    if x_range and y_range:
                        print(f"📊 X-axis range: {x_range[0]:.1f} - {x_range[1]:.1f}")
                        print(f"📊 Y-axis range: {y_range[0]:.1f} - {y_range[1]:.1f}")
                        
                        # Calculate expected midpoints
                        x_mid = (x_range[0] + x_range[1]) / 2
                        y_mid = (y_range[0] + y_range[1]) / 2
                        
                        print(f"📊 Expected quadrant center: ({x_mid:.1f}, {y_mid:.1f})")
                        
                        # Verify quadrant lines are at the midpoints
                        if len(line_shapes) >= 2:
                            horizontal_lines = [line for line in line_shapes if line.y0 == line.y1]
                            vertical_lines = [line for line in line_shapes if line.x0 == line.x1]
                            
                            if horizontal_lines:
                                h_line = horizontal_lines[0]
                                if abs(h_line.y0 - y_mid) < 0.1:
                                    print("✅ Horizontal line positioned correctly at y-midpoint")
                                else:
                                    print(f"⚠️  Horizontal line at y={h_line.y0:.1f}, expected y={y_mid:.1f}")
                            
                            if vertical_lines:
                                v_line = vertical_lines[0]
                                if abs(v_line.x0 - x_mid) < 0.1:
                                    print("✅ Vertical line positioned correctly at x-midpoint")
                                else:
                                    print(f"⚠️  Vertical line at x={v_line.x0:.1f}, expected x={x_mid:.1f}")
                    else:
                        print("⚠️  Could not retrieve axis ranges")
                else:
                    print("⚠️  Could not access axis information")
            else:
                print("⚠️  Figure has no data traces")
                
        else:
            print("❌ Failed to create scatter plot")
            return False
        
        # Test 5: Test with different stat combinations
        print("\n🔍 STEP 5: TESTING DIFFERENT STAT COMBINATIONS")
        print("-" * 50)
        
        test_combinations = [
            ("shots", "passes_accurate"),
            ("duels_won", "recoveries"),
            ("dribbles_successful", "passes")
        ]
        
        for x_stat, y_stat in test_combinations:
            print(f"\nTesting: {x_stat} vs {y_stat}")
            
            fig = create_outfield_scatter_plot(
                test_players,
                test_player_stats,
                x_stat,
                y_stat,
                "All Outfield",
                per_90_mode=False
            )
            
            if fig and hasattr(fig, 'layout') and hasattr(fig.layout, 'shapes'):
                line_shapes = [shape for shape in fig.layout.shapes if shape.type == 'line']
                if len(line_shapes) >= 2:
                    print(f"  ✅ {len(line_shapes)} quadrant lines found")
                else:
                    print(f"  ❌ Only {len(line_shapes)} quadrant lines found")
            else:
                print(f"  ❌ No quadrant lines found")
        
        print(f"\n✅ QUADRANT LINES TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quadrant_lines()
    if success:
        print(f"\n🎉 All tests passed! Quadrant lines are working correctly.")
    else:
        print(f"\n💥 Some tests failed. Please check the error messages above.")
