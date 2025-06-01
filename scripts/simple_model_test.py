#!/usr/bin/env python3
"""
Simple test to verify model change to phi3:mini.
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

def test_model_change():
    """Test that RAG systems use phi3:mini."""
    print("Testing model change to phi3:mini...")
    
    try:
        # Test GoalkeeperRAG
        from core.rag_system import GoalkeeperRAG
        gk_rag = GoalkeeperRAG()
        
        if gk_rag.model_name == "phi3:mini":
            print("✅ GoalkeeperRAG uses phi3:mini")
        else:
            print(f"❌ GoalkeeperRAG uses {gk_rag.model_name}")
            return False
        
        # Test OutfieldRAG
        from core.rag_system import OutfieldRAG
        outfield_rag = OutfieldRAG()
        
        if outfield_rag.model_name == "phi3:mini":
            print("✅ OutfieldRAG uses phi3:mini")
        else:
            print(f"❌ OutfieldRAG uses {outfield_rag.model_name}")
            return False
        
        print("✅ Model change successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_model_change()
    if success:
        print("🎉 Model change test passed!")
    else:
        print("💥 Model change test failed!")
