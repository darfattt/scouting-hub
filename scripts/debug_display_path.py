#!/usr/bin/env python3
"""
Debug the exact display path to see where shot accuracy gets lost.
This script simulates the exact Streamlit app flow.
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

def debug_display_path():
    """Debug the exact display path used in the Streamlit app."""
    print("=" * 80)
    print("DEBUGGING DISPLAY PATH")
    print("=" * 80)
    
    try:
        # Step 1: Simulate app.py data loading
        print("\n🔍 STEP 1: SIMULATING APP.PY DATA LOADING")
        print("-" * 50)
        
        from core.data_processor import OutfieldDataProcessor
        
        # This is exactly what app.py does
        outfield_processor = OutfieldDataProcessor()
        outfield_data = outfield_processor.process_data()
        
        print(f"Loaded {len(outfield_data)} outfield players")
        
        # Check first player's shot accuracy
        first_player = list(outfield_data.keys())[0]
        first_player_stats = outfield_data[first_player]
        
        print(f"First player: {first_player}")
        print(f"Shot accuracy in outfield_data: {first_player_stats.get('shot_accuracy', 'NOT_FOUND')}")
        
        # Step 2: Simulate the filtering that happens in app.py
        print("\n🔍 STEP 2: SIMULATING APP.PY FILTERING")
        print("-" * 50)
        
        # This simulates the global filtering that happens in app.py
        filtered_data = {}
        for player_name, stats in outfield_data.items():
            # Apply any filters (date, competition, etc.)
            # For now, just copy all data
            filtered_data[player_name] = stats.copy()
        
        print(f"Filtered data has {len(filtered_data)} players")
        
        # Check if shot accuracy is preserved
        first_filtered_stats = filtered_data[first_player]
        print(f"Shot accuracy in filtered_data: {first_filtered_stats.get('shot_accuracy', 'NOT_FOUND')}")
        
        # Step 3: Simulate the render_outfield_player_search function
        print("\n🔍 STEP 3: SIMULATING RENDER_OUTFIELD_PLAYER_SEARCH")
        print("-" * 50)
        
        # This is the exact code from outfield_components.py
        position_type = "All Outfield"
        
        # Filter players by position (this is done in the actual function)
        filtered_players = list(filtered_data.keys())
        
        print(f"Position type: {position_type}")
        print(f"Filtered players: {len(filtered_players)}")
        
        # Create table data exactly as done in the function
        data = []
        for player in filtered_players[:3]:  # Test first 3 players
            stats = filtered_data[player]
            
            print(f"\nProcessing player: {player}")
            print(f"  Raw shot_accuracy: {stats.get('shot_accuracy', 'NOT_FOUND')}")
            
            # Create row data exactly as in outfield_components.py
            row_data = {
                "Player": player,
                "Team": stats.get("team", "Unknown"),
                "Position": stats.get("position", "Unknown"),
                "Matches": stats.get("matches", 0),
                "Minutes": stats.get("minutes", 0),
                "Goals": stats.get("goals", 0),
                "Assists": stats.get("assists", 0),
                "Pass Accuracy": f"{stats.get('pass_accuracy', 0):.1f}%"
            }
            
            # Add position-specific stats (exact code from outfield_components.py)
            if position_type in ["Forwards", "All Outfield"]:
                # Use pre-calculated shot accuracy from data_processor.py
                shot_accuracy_val = stats.get('shot_accuracy', 0)
                row_data["Shot Accuracy"] = f"{shot_accuracy_val:.1f}%"
                
                print(f"  shot_accuracy_val: {shot_accuracy_val}")
                print(f"  Formatted Shot Accuracy: {row_data['Shot Accuracy']}")
            
            data.append(row_data)
        
        # Step 4: Display the final table data
        print("\n🔍 STEP 4: FINAL TABLE DATA")
        print("-" * 50)
        
        print(f"{'Player':<20} {'Position':<10} {'Goals':<6} {'Shot Accuracy':<12}")
        print("-" * 60)
        
        for row in data:
            shot_acc = row.get("Shot Accuracy", "N/A")
            print(f"{row['Player']:<20} {row['Position']:<10} {row['Goals']:<6} {shot_acc:<12}")
        
        # Step 5: Check if there's any data transformation issue
        print("\n🔍 STEP 5: CHECKING FOR DATA TRANSFORMATION ISSUES")
        print("-" * 50)
        
        # Check if the data is being modified somewhere
        for player in filtered_players[:3]:
            original_stats = outfield_data[player]
            filtered_stats = filtered_data[player]
            
            original_accuracy = original_stats.get('shot_accuracy', 0)
            filtered_accuracy = filtered_stats.get('shot_accuracy', 0)
            
            print(f"Player: {player}")
            print(f"  Original accuracy: {original_accuracy}")
            print(f"  Filtered accuracy: {filtered_accuracy}")
            print(f"  Match: {'✅' if original_accuracy == filtered_accuracy else '❌'}")
        
        # Step 6: Test with different position types
        print("\n🔍 STEP 6: TESTING DIFFERENT POSITION TYPES")
        print("-" * 50)
        
        position_types = ["All Outfield", "Forwards", "Midfielders", "Defenders"]
        
        for pos_type in position_types:
            print(f"\nTesting position type: {pos_type}")
            
            # Check if shot accuracy is shown for this position type
            if pos_type in ["Forwards", "All Outfield"]:
                print(f"  ✅ Shot accuracy should be shown for {pos_type}")
                
                # Test the exact condition
                test_stats = filtered_data[first_player]
                shot_accuracy_val = test_stats.get('shot_accuracy', 0)
                formatted = f"{shot_accuracy_val:.1f}%"
                print(f"  Shot accuracy value: {shot_accuracy_val}")
                print(f"  Formatted: {formatted}")
            else:
                print(f"  ❌ Shot accuracy not shown for {pos_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_display_path()
    if success:
        print(f"\n✅ Display path debugging completed!")
    else:
        print(f"\n❌ Display path debugging failed!")
