#!/usr/bin/env python3
"""
Clear Streamlit cache to force reload of data after changes.
This script helps resolve caching issues when data processing logic is updated.
"""

import os
import sys
import shutil

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def clear_streamlit_cache():
    """Clear Streamlit cache and related files."""
    print("=" * 60)
    print("CLEARING STREAMLIT CACHE")
    print("=" * 60)
    
    cache_locations = [
        ".streamlit",
        "__pycache__",
        "src/__pycache__",
        "src/core/__pycache__",
        "src/components/__pycache__",
        "storage/player_data.pkl",
        "storage/tfidf_model.pkl",
        "player_data.pkl",
        "tfidf_model.pkl"
    ]
    
    cleared_count = 0
    
    for cache_path in cache_locations:
        if os.path.exists(cache_path):
            try:
                if os.path.isdir(cache_path):
                    shutil.rmtree(cache_path)
                    print(f"✅ Removed directory: {cache_path}")
                else:
                    os.remove(cache_path)
                    print(f"✅ Removed file: {cache_path}")
                cleared_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {cache_path}: {e}")
        else:
            print(f"⚪ Not found: {cache_path}")
    
    print(f"\n📊 Cleared {cleared_count} cache items")
    
    # Also clear Python bytecode files
    print(f"\n🔍 Clearing Python bytecode files...")
    
    bytecode_count = 0
    for root, dirs, files in os.walk("."):
        # Skip .venv and .git directories
        dirs[:] = [d for d in dirs if d not in ['.venv', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    bytecode_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")
    
    if bytecode_count > 0:
        print(f"✅ Removed {bytecode_count} Python bytecode files")
    else:
        print(f"⚪ No Python bytecode files found")

def rebuild_data():
    """Rebuild the data to ensure fresh processing."""
    print(f"\n🔄 REBUILDING DATA")
    print("-" * 40)
    
    try:
        from core.data_processor import OutfieldDataProcessor
        
        # Force rebuild outfield data
        processor = OutfieldDataProcessor()
        player_data = processor.process_data()
        
        print(f"✅ Rebuilt outfield data for {len(player_data)} players")
        
        # Check shot accuracy for first player
        if player_data:
            first_player = list(player_data.keys())[0]
            shot_accuracy = player_data[first_player].get('shot_accuracy', 0)
            print(f"✅ Sample shot accuracy: {first_player} = {shot_accuracy:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to rebuild data: {e}")
        return False

def main():
    """Main function to clear cache and rebuild data."""
    print("🧹 STREAMLIT CACHE CLEANER")
    print("This script will clear all cached data and force fresh data processing.")
    print()
    
    # Step 1: Clear cache
    clear_streamlit_cache()
    
    # Step 2: Rebuild data
    rebuild_success = rebuild_data()
    
    # Step 3: Instructions
    print(f"\n📋 NEXT STEPS:")
    print("-" * 40)
    
    if rebuild_success:
        print("✅ Cache cleared and data rebuilt successfully!")
        print()
        print("1. Restart your Streamlit app:")
        print("   - Stop the current app (Ctrl+C)")
        print("   - Run: streamlit run app.py")
        print()
        print("2. Or clear browser cache:")
        print("   - Press Ctrl+F5 or Cmd+Shift+R")
        print("   - Or open in incognito/private mode")
        print()
        print("3. Navigate to Player Search:")
        print("   - Select 'All Outfield' or 'Forwards'")
        print("   - Check the 'Shot Accuracy' column")
        print("   - You should now see values like 47.0%, 45.0%, etc.")
    else:
        print("❌ Cache cleared but data rebuild failed!")
        print()
        print("1. Check for errors above")
        print("2. Try running: python scripts/build_all_rag.py")
        print("3. Then restart Streamlit app")
    
    print(f"\n🎯 Expected Result:")
    print("Shot accuracy should show realistic values (not 0.0%) in Player Search table")

if __name__ == "__main__":
    main()
