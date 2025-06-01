#!/usr/bin/env python3
"""
Simple test to verify scatter plot fix works.
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

def simple_test():
    """Simple test of scatter plot function."""
    print("Testing scatter plot fix...")
    
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
            return True
        else:
            print("❌ Failed to create scatter plot")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("🎉 Test passed!")
    else:
        print("💥 Test failed!")
