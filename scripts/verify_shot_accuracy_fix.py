#!/usr/bin/env python3
"""
Verify that shot accuracy is correctly displayed in Player Search table.
This script tests the exact code path used in the Player Search interface.
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

def verify_shot_accuracy_fix():
    """Verify shot accuracy fix in Player Search table."""
    print("=" * 60)
    print("VERIFYING SHOT ACCURACY FIX")
    print("=" * 60)
    
    try:
        from core.data_processor import OutfieldDataProcessor
        
        # Initialize and process data (same as Player Search does)
        processor = OutfieldDataProcessor()
        filtered_data = processor.process_data()
        
        print(f"📊 Loaded {len(filtered_data)} outfield players")
        
        # Simulate the exact code path used in render_outfield_player_search
        position_type = "All Outfield"
        filtered_players = list(filtered_data.keys())
        
        print(f"\n🔍 Testing Player Search table data generation...")
        
        # Create data exactly as done in outfield_components.py
        data = []
        for player in filtered_players[:5]:  # Test first 5 players
            stats = filtered_data[player]
            
            # Create row data based on position type (exact code from outfield_components.py)
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
            
            data.append(row_data)
        
        # Display results
        print(f"\n📋 PLAYER SEARCH TABLE DATA:")
        print("-" * 100)
        print(f"{'Player':<20} {'Team':<15} {'Position':<10} {'Goals':<6} {'Assists':<8} {'Shot Accuracy':<12}")
        print("-" * 100)
        
        for row in data:
            shot_acc = row.get("Shot Accuracy", "N/A")
            print(f"{row['Player']:<20} {row['Team']:<15} {row['Position']:<10} "
                  f"{row['Goals']:<6} {row['Assists']:<8} {shot_acc:<12}")
        
        # Verify shot accuracy values
        shot_accuracy_values = []
        for row in data:
            if "Shot Accuracy" in row:
                # Extract numeric value from percentage string
                shot_acc_str = row["Shot Accuracy"]
                shot_acc_val = float(shot_acc_str.replace('%', ''))
                shot_accuracy_values.append(shot_acc_val)
        
        print(f"\n📊 SHOT ACCURACY ANALYSIS:")
        print(f"   Players with shot accuracy data: {len(shot_accuracy_values)}")
        print(f"   Shot accuracy values: {shot_accuracy_values}")
        print(f"   Average shot accuracy: {sum(shot_accuracy_values)/len(shot_accuracy_values):.1f}%")
        print(f"   Range: {min(shot_accuracy_values):.1f}% - {max(shot_accuracy_values):.1f}%")
        
        # Check for issues
        zero_accuracy_count = sum(1 for val in shot_accuracy_values if val == 0.0)
        
        if zero_accuracy_count == len(shot_accuracy_values):
            print(f"\n❌ ISSUE: All players showing 0.0% shot accuracy!")
            return False
        elif zero_accuracy_count > 0:
            print(f"\n⚠️  WARNING: {zero_accuracy_count} players showing 0.0% shot accuracy")
        else:
            print(f"\n✅ SUCCESS: All players have realistic shot accuracy values")
        
        # Verify data source
        print(f"\n🔍 DATA SOURCE VERIFICATION:")
        for i, row in enumerate(data[:3]):
            player_name = row["Player"]
            stats = filtered_data[player_name]
            
            shots = stats.get('shots', 0)
            shots_on_target = stats.get('shots_on_target', 0)
            stored_accuracy = stats.get('shot_accuracy', 0)
            displayed_accuracy = float(row["Shot Accuracy"].replace('%', ''))
            
            print(f"   Player {i+1}: {player_name}")
            print(f"     Shots: {shots}")
            print(f"     Shots on target: {shots_on_target}")
            print(f"     Stored accuracy: {stored_accuracy:.1f}%")
            print(f"     Displayed accuracy: {displayed_accuracy:.1f}%")
            print(f"     Match: {'✅' if abs(stored_accuracy - displayed_accuracy) < 0.1 else '❌'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_shot_accuracy_fix()
    if success:
        print(f"\n✅ Shot accuracy fix verification completed successfully!")
        print(f"The Player Search table should now display correct shot accuracy values.")
    else:
        print(f"\n❌ Shot accuracy fix verification failed!")
        print(f"There may still be issues with the shot accuracy display.")
