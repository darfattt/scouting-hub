#!/usr/bin/env python3
"""
Debug script to check shot accuracy calculation issue.
This script will examine the actual column names and data in CSV files.
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

def debug_shot_accuracy():
    """Debug shot accuracy calculation."""
    print("=" * 60)
    print("DEBUGGING SHOT ACCURACY CALCULATION")
    print("=" * 60)
    
    data_dir = "data/stats"
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"❌ No CSV files found in {data_dir}")
        return
    
    print(f"📁 Found {len(csv_files)} CSV files")
    
    # Check first few files for column names
    for i, filename in enumerate(csv_files[:3]):
        print(f"\n📄 File {i+1}: {filename}")
        file_path = os.path.join(data_dir, filename)
        
        try:
            df = pd.read_csv(file_path)
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            
            # Check for shot-related columns
            shot_columns = [col for col in df.columns if 'shot' in col.lower()]
            print(f"   Shot-related columns: {shot_columns}")
            
            # Check for specific columns we're looking for
            target_columns = ['Shots', 'Shots On Target', 'Shots on target', 'shots on target']
            found_columns = []
            for col in target_columns:
                if col in df.columns:
                    found_columns.append(col)
            
            print(f"   Found target columns: {found_columns}")
            
            # Show sample data for shot columns
            if shot_columns:
                print(f"   Sample data for shot columns:")
                for col in shot_columns:
                    sample_values = df[col].dropna().head(3).tolist()
                    print(f"     {col}: {sample_values}")
            
            # Check if there are any non-zero values
            if 'Shots' in df.columns:
                total_shots = df['Shots'].sum()
                print(f"   Total shots in file: {total_shots}")
            
            if 'Shots On Target' in df.columns:
                total_shots_on_target = df['Shots On Target'].sum()
                print(f"   Total shots on target: {total_shots_on_target}")
            elif 'Shots on target' in df.columns:
                total_shots_on_target = df['Shots on target'].sum()
                print(f"   Total shots on target: {total_shots_on_target}")
            
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    
    # Now test with the data processor
    print(f"\n🔍 Testing with OutfieldDataProcessor...")
    
    try:
        from core.data_processor import OutfieldDataProcessor
        
        processor = OutfieldDataProcessor()
        processor.process_data()
        
        # Check a few players for shot accuracy
        players_checked = 0
        for player_name, player_data in processor.player_data.items():
            if players_checked >= 3:
                break
                
            shots = player_data.get('shots', 0)
            shots_on_target = player_data.get('shots_on_target', 0)
            shot_accuracy = player_data.get('shot_accuracy', 0)
            
            print(f"\n👤 Player: {player_name}")
            print(f"   Shots: {shots}")
            print(f"   Shots on target: {shots_on_target}")
            print(f"   Shot accuracy: {shot_accuracy}%")
            
            if shots > 0 and shots_on_target == 0:
                print(f"   ⚠️  Issue: Player has shots but no shots on target!")
            elif shots > 0 and shot_accuracy == 0:
                print(f"   ⚠️  Issue: Player has shots but 0% accuracy!")
            elif shots > 0 and shot_accuracy > 0:
                print(f"   ✅ Shot accuracy calculation working correctly")
            
            players_checked += 1
            
    except Exception as e:
        print(f"❌ Error with data processor: {e}")
        import traceback
        traceback.print_exc()

def check_all_columns():
    """Check all columns in the first CSV file."""
    print(f"\n📋 ALL COLUMNS IN FIRST CSV FILE:")
    print("=" * 60)
    
    data_dir = "data/stats"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if csv_files:
        file_path = os.path.join(data_dir, csv_files[0])
        df = pd.read_csv(file_path)
        
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")

if __name__ == "__main__":
    debug_shot_accuracy()
    check_all_columns()
