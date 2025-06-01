#!/usr/bin/env python3
"""
Simple test to verify quadrant lines are added to scatter plots.
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

def simple_quadrant_test():
    """Simple test of quadrant lines in scatter plot."""
    print("Testing quadrant lines...")
    
    try:
        # Test import
        from components.outfield_components import create_outfield_scatter_plot
        print("✅ Import successful")
        
        # Test with mock data
        test_players = ["Player A", "Player B", "Player C"]
        test_stats = [
            {"goals": 10, "assists": 5},
            {"goals": 8, "assists": 7},
            {"goals": 12, "assists": 3}
        ]
        
        # Test function call
        fig = create_outfield_scatter_plot(
            test_players,
            test_stats,
            "goals",
            "assists",
            "All Outfield",
            per_90_mode=False
        )
        
        if fig:
            print("✅ Scatter plot created successfully")
            
            # Check for shapes (quadrant lines)
            if hasattr(fig, 'layout') and hasattr(fig.layout, 'shapes'):
                shapes = fig.layout.shapes
                line_shapes = [shape for shape in shapes if shape.type == 'line']
                
                print(f"📊 Found {len(line_shapes)} line shapes")
                
                if len(line_shapes) >= 2:
                    print("✅ Quadrant lines detected!")
                    return True
                else:
                    print("❌ No quadrant lines found")
                    return False
            else:
                print("❌ No shapes in plot layout")
                return False
        else:
            print("❌ Failed to create scatter plot")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = simple_quadrant_test()
    if success:
        print("🎉 Quadrant lines test passed!")
    else:
        print("💥 Quadrant lines test failed!")
