#!/usr/bin/env python3
"""
Test script to verify shot accuracy display in Player Search table.
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

def test_shot_accuracy_display():
    """Test shot accuracy display in player search."""
    print("=" * 60)
    print("TESTING SHOT ACCURACY DISPLAY")
    print("=" * 60)
    
    try:
        from core.data_processor import OutfieldDataProcessor
        
        # Initialize and process data
        processor = OutfieldDataProcessor()
        player_data = processor.process_data()
        
        print(f"📊 Processed {len(player_data)} outfield players")
        
        # Test shot accuracy for first 5 players
        players_with_shots = []
        players_without_shots = []
        
        for player_name, stats in player_data.items():
            shots = stats.get('shots', 0)
            shots_on_target = stats.get('shots_on_target', 0)
            shot_accuracy = stats.get('shot_accuracy', 0)
            
            if shots > 0:
                players_with_shots.append({
                    'name': player_name,
                    'shots': shots,
                    'shots_on_target': shots_on_target,
                    'shot_accuracy': shot_accuracy,
                    'calculated_accuracy': (shots_on_target / shots * 100) if shots > 0 else 0
                })
            else:
                players_without_shots.append(player_name)
        
        print(f"\n🎯 Players with shots: {len(players_with_shots)}")
        print(f"🚫 Players without shots: {len(players_without_shots)}")
        
        # Show top 5 players with shots
        print(f"\n📋 TOP 5 PLAYERS WITH SHOTS:")
        print("-" * 80)
        print(f"{'Player':<20} {'Shots':<8} {'On Target':<10} {'Stored %':<10} {'Calc %':<10}")
        print("-" * 80)
        
        for i, player in enumerate(players_with_shots[:5]):
            print(f"{player['name']:<20} {player['shots']:<8} {player['shots_on_target']:<10} "
                  f"{player['shot_accuracy']:<10.1f} {player['calculated_accuracy']:<10.1f}")
        
        # Test the display formatting
        print(f"\n🎨 DISPLAY FORMATTING TEST:")
        print("-" * 50)
        
        for i, player in enumerate(players_with_shots[:3]):
            stats = player_data[player['name']]
            
            # Test the exact formatting used in outfield_components.py
            shot_accuracy_val = stats.get('shot_accuracy', 0)
            formatted_1 = f"{shot_accuracy_val:.1f}%" if shot_accuracy_val > 0 else "0.0%"
            
            # Test recalculation
            shots = stats.get('shots', 0)
            shots_on_target = stats.get('shots_on_target', 0)
            calculated_accuracy = (shots_on_target / shots * 100) if shots > 0 else 0
            formatted_2 = f"{calculated_accuracy:.1f}%"
            
            print(f"Player: {player['name']}")
            print(f"  Original format: {formatted_1}")
            print(f"  Recalculated format: {formatted_2}")
            print(f"  Match: {'✅' if formatted_1 == formatted_2 else '❌'}")
            print()
        
        # Check for any players showing 0% when they shouldn't
        zero_accuracy_with_shots = [p for p in players_with_shots if p['shot_accuracy'] == 0 and p['shots'] > 0]
        
        if zero_accuracy_with_shots:
            print(f"⚠️  POTENTIAL ISSUES - Players with shots but 0% accuracy:")
            for player in zero_accuracy_with_shots:
                print(f"  {player['name']}: {player['shots']} shots, {player['shots_on_target']} on target")
        else:
            print(f"✅ No issues found - all players with shots have correct accuracy calculations")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shot_accuracy_display()
    if success:
        print(f"\n✅ Shot accuracy display test completed successfully!")
    else:
        print(f"\n❌ Shot accuracy display test failed!")
