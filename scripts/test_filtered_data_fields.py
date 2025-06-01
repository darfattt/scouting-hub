#!/usr/bin/env python3
"""
Test script to verify that all fields from data_processor.py are now included in filtered_data.
This script compares the fields between original data and filtered data.
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

def test_filtered_data_fields():
    """Test that filtered data includes all fields from data processor."""
    print("=" * 80)
    print("TESTING FILTERED DATA FIELDS")
    print("=" * 80)
    
    try:
        from core.data_processor import OutfieldDataProcessor
        from components.app_components import filter_player_data
        
        # Step 1: Get original data from processor
        print("\n🔍 STEP 1: GETTING ORIGINAL DATA FROM PROCESSOR")
        print("-" * 50)
        
        processor = OutfieldDataProcessor()
        original_data = processor.process_data()
        
        print(f"Original data loaded: {len(original_data)} players")
        
        # Get first player's fields
        first_player = list(original_data.keys())[0]
        original_fields = set(original_data[first_player].keys())
        
        print(f"Original fields count: {len(original_fields)}")
        print(f"Sample player: {first_player}")
        
        # Step 2: Create a mock RAG object for filtering
        print("\n🔍 STEP 2: CREATING FILTERED DATA")
        print("-" * 50)
        
        class MockRAG:
            def __init__(self, data):
                self.data_processor = MockDataProcessor(data)
        
        class MockDataProcessor:
            def __init__(self, data):
                self.player_data = data
        
        mock_rag = MockRAG(original_data)
        
        # Create mock filters (no filtering)
        filters = {
            "use_date_filter": False,
            "start_date": None,
            "end_date": None
        }
        
        # Apply filtering
        filtered_data = filter_player_data(mock_rag, filters)
        
        print(f"Filtered data: {len(filtered_data)} players")
        
        # Step 3: Compare fields
        print("\n🔍 STEP 3: COMPARING FIELDS")
        print("-" * 50)
        
        if first_player in filtered_data:
            filtered_fields = set(filtered_data[first_player].keys())
            
            print(f"Filtered fields count: {len(filtered_fields)}")
            
            # Find missing fields
            missing_fields = original_fields - filtered_fields
            extra_fields = filtered_fields - original_fields
            
            print(f"\n📊 FIELD COMPARISON:")
            print(f"   Original fields: {len(original_fields)}")
            print(f"   Filtered fields: {len(filtered_fields)}")
            print(f"   Missing fields: {len(missing_fields)}")
            print(f"   Extra fields: {len(extra_fields)}")
            
            if missing_fields:
                print(f"\n❌ MISSING FIELDS ({len(missing_fields)}):")
                for field in sorted(missing_fields):
                    print(f"   - {field}")
            else:
                print(f"\n✅ NO MISSING FIELDS!")
            
            if extra_fields:
                print(f"\n➕ EXTRA FIELDS ({len(extra_fields)}):")
                for field in sorted(extra_fields):
                    print(f"   + {field}")
            
            # Step 4: Test shot accuracy specifically
            print(f"\n🎯 SHOT ACCURACY TEST:")
            print("-" * 30)
            
            original_shot_accuracy = original_data[first_player].get('shot_accuracy', 'NOT_FOUND')
            filtered_shot_accuracy = filtered_data[first_player].get('shot_accuracy', 'NOT_FOUND')
            
            print(f"Original shot accuracy: {original_shot_accuracy}")
            print(f"Filtered shot accuracy: {filtered_shot_accuracy}")
            
            if original_shot_accuracy == filtered_shot_accuracy:
                print(f"✅ Shot accuracy preserved correctly!")
            else:
                print(f"❌ Shot accuracy mismatch!")
            
            # Step 5: Test other important fields
            print(f"\n🔍 IMPORTANT FIELDS TEST:")
            print("-" * 30)
            
            important_fields = [
                'xg', 'total_actions', 'total_actions_successful',
                'long_passes', 'long_passes_accurate', 'crosses', 'crosses_accurate',
                'aerial_duels', 'aerial_duels_won', 'losses', 'losses_own_half',
                'recoveries_opp_half', 'long_pass_accuracy', 'cross_accuracy',
                'aerial_duel_success_rate', 'shots_per_90', 'xg_per_90'
            ]
            
            for field in important_fields:
                original_val = original_data[first_player].get(field, 'NOT_FOUND')
                filtered_val = filtered_data[first_player].get(field, 'NOT_FOUND')
                
                if original_val == filtered_val:
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"   {status} {field}: {original_val} -> {filtered_val}")
            
            return len(missing_fields) == 0
        else:
            print(f"❌ First player not found in filtered data!")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_filtered_data_fields()
    if success:
        print(f"\n✅ All fields are properly included in filtered data!")
        print(f"The shot accuracy issue should now be resolved.")
    else:
        print(f"\n❌ Some fields are still missing from filtered data!")
        print(f"Additional fixes may be needed.")
