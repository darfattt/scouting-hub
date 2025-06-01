#!/usr/bin/env python3
"""
Test script to verify the AI insights functionality in Find Similar Player feature.
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

def test_ai_insights_import():
    """Test that the AI insights function can be imported."""
    print("🔍 TESTING AI INSIGHTS IMPORT")
    print("-" * 50)
    
    try:
        from components.player_clone_components import generate_similarity_insights
        
        print("✅ Successfully imported generate_similarity_insights function")
        
        # Check if function is callable
        if callable(generate_similarity_insights):
            print("✅ generate_similarity_insights is callable")
        else:
            print("❌ generate_similarity_insights is not callable")
            return False
        
        # Check function signature
        import inspect
        sig = inspect.signature(generate_similarity_insights)
        expected_params = ['selected_player', 'top_players', 'selected_stats', 'per_90_mode', 'player_data']
        actual_params = list(sig.parameters.keys())
        
        if actual_params == expected_params:
            print("✅ Function signature is correct")
        else:
            print(f"❌ Function signature mismatch. Expected: {expected_params}, Got: {actual_params}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing AI insights function: {e}")
        return False

def test_ai_insights_generation():
    """Test the AI insights generation with mock data."""
    print("\n🔍 TESTING AI INSIGHTS GENERATION")
    print("-" * 50)
    
    try:
        from components.player_clone_components import generate_similarity_insights
        
        # Create comprehensive mock data
        mock_player_data = {
            "Lionel Messi": {
                "goals": 25, "assists": 15, "shots": 120, "passes": 2000,
                "minutes": 2700, "age": 36, "team": "Inter Miami", "position": "RW",
                "match_data": [
                    {"Date": "2024-01-15", "Competition": "MLS"},
                    {"Date": "2024-02-20", "Competition": "MLS"}
                ]
            },
            "Mohamed Salah": {
                "goals": 22, "assists": 12, "shots": 110, "passes": 1800,
                "minutes": 2500, "age": 31, "team": "Liverpool", "position": "RW",
                "match_data": [
                    {"Date": "2024-01-10", "Competition": "Premier League"},
                    {"Date": "2024-02-15", "Competition": "Premier League"}
                ]
            },
            "Kylian Mbappe": {
                "goals": 28, "assists": 8, "shots": 130, "passes": 1500,
                "minutes": 2400, "age": 25, "team": "PSG", "position": "LW",
                "match_data": [
                    {"Date": "2024-01-05", "Competition": "Ligue 1"}
                ]
            },
            "Vinicius Jr": {
                "goals": 18, "assists": 10, "shots": 95, "passes": 1600,
                "minutes": 2200, "age": 23, "team": "Real Madrid", "position": "LW",
                "match_data": [
                    {"Date": "2024-01-08", "Competition": "La Liga"}
                ]
            }
        }
        
        # Mock top similar players (player_name, similarity_score)
        mock_top_players = [
            ("Mohamed Salah", 0.92),
            ("Kylian Mbappe", 0.85),
            ("Vinicius Jr", 0.78)
        ]
        
        # Mock selected stats
        mock_selected_stats = ["goals", "assists", "shots"]
        
        print("✅ Mock data prepared")
        print(f"✅ Selected player: Lionel Messi")
        print(f"✅ Top similar players: {len(mock_top_players)}")
        print(f"✅ Selected stats: {mock_selected_stats}")
        
        # Test normal mode insights
        insights_normal = generate_similarity_insights(
            "Lionel Messi",
            mock_top_players,
            mock_selected_stats,
            per_90_mode=False,
            player_data=mock_player_data
        )
        
        if insights_normal and len(insights_normal) > 100:  # Should be substantial content
            print("✅ Normal mode insights generated successfully")
            print(f"✅ Insights length: {len(insights_normal)} characters")
        else:
            print(f"❌ Normal mode insights too short or empty: {len(insights_normal) if insights_normal else 0} characters")
            return False
        
        # Test per 90 mode insights
        insights_per90 = generate_similarity_insights(
            "Lionel Messi",
            mock_top_players,
            mock_selected_stats,
            per_90_mode=True,
            player_data=mock_player_data
        )
        
        if insights_per90 and len(insights_per90) > 100:  # Should be substantial content
            print("✅ Per 90 mode insights generated successfully")
            print(f"✅ Insights length: {len(insights_per90)} characters")
        else:
            print(f"❌ Per 90 mode insights too short or empty: {len(insights_per90) if insights_per90 else 0} characters")
            return False
        
        # Check that insights contain expected sections
        expected_sections = [
            "🎯 Similarity Analysis",
            "💪 Strongest Statistical Attributes", 
            "🔍 Most Similar Players",
            "🧠 Key Insights",
            "💡 Recommendations"
        ]
        
        sections_found = 0
        for section in expected_sections:
            if section in insights_normal:
                sections_found += 1
        
        if sections_found == len(expected_sections):
            print("✅ All expected sections found in insights")
        else:
            print(f"❌ Missing sections. Found {sections_found}/{len(expected_sections)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI insights generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_insights_content_quality():
    """Test the quality and structure of generated insights."""
    print("\n🔍 TESTING INSIGHTS CONTENT QUALITY")
    print("-" * 50)
    
    try:
        from components.player_clone_components import generate_similarity_insights
        
        # Create mock data with different similarity patterns
        mock_player_data = {
            "Player A": {
                "goals": 20, "assists": 10, "shots": 100, "passes": 1500,
                "minutes": 2000, "age": 25, "team": "Team A", "position": "CF",
                "match_data": [{"Date": "2024-01-15", "Competition": "Liga 1"}]
            },
            "Player B": {  # High similarity
                "goals": 19, "assists": 11, "shots": 95, "passes": 1450,
                "minutes": 1950, "age": 26, "team": "Team B", "position": "CF",
                "match_data": [{"Date": "2024-01-10", "Competition": "Liga 1"}]
            },
            "Player C": {  # Medium similarity
                "goals": 15, "assists": 8, "shots": 80, "passes": 1200,
                "minutes": 1800, "age": 24, "team": "Team C", "position": "CF",
                "match_data": [{"Date": "2024-01-05", "Competition": "Liga 1"}]
            },
            "Player D": {  # Lower similarity, different position
                "goals": 12, "assists": 6, "shots": 70, "passes": 1000,
                "minutes": 1600, "age": 28, "team": "Team D", "position": "LW",
                "match_data": [{"Date": "2024-01-08", "Competition": "Liga 1"}]
            }
        }
        
        # Mock with different similarity scores
        mock_top_players = [
            ("Player B", 0.95),  # High similarity
            ("Player C", 0.72),  # Medium similarity  
            ("Player D", 0.58)   # Lower similarity
        ]
        
        mock_selected_stats = ["goals", "assists", "shots"]
        
        # Generate insights
        insights = generate_similarity_insights(
            "Player A",
            mock_top_players,
            mock_selected_stats,
            per_90_mode=False,
            player_data=mock_player_data
        )
        
        print("✅ Insights generated for quality testing")
        
        # Test content quality checks
        quality_checks = [
            ("Player profile information", "Player Profile:" in insights),
            ("Similarity percentages", "95.0% similarity" in insights),
            ("Statistical comparisons", "vs" in insights),
            ("Key insights section", "Key Insights" in insights),
            ("Recommendations section", "Recommendations" in insights),
            ("Best match identification", "Best Match" in insights),
            ("Similarity pattern analysis", "Strong Similarity Pattern" in insights or "Moderate Similarity" in insights)
        ]
        
        passed_checks = 0
        for check_name, check_result in quality_checks:
            if check_result:
                print(f"✅ {check_name}: Found")
                passed_checks += 1
            else:
                print(f"❌ {check_name}: Missing")
        
        if passed_checks >= len(quality_checks) - 1:  # Allow 1 missing check
            print(f"✅ Content quality acceptable: {passed_checks}/{len(quality_checks)} checks passed")
        else:
            print(f"❌ Content quality insufficient: {passed_checks}/{len(quality_checks)} checks passed")
            return False
        
        # Test markdown formatting
        markdown_elements = ["##", "###", "**", "*", "-"]
        markdown_found = sum(1 for element in markdown_elements if element in insights)
        
        if markdown_found >= 3:
            print("✅ Proper markdown formatting detected")
        else:
            print(f"❌ Insufficient markdown formatting: {markdown_found}/5 elements found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing insights content quality: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases for AI insights generation."""
    print("\n🔍 TESTING EDGE CASES")
    print("-" * 50)
    
    try:
        from components.player_clone_components import generate_similarity_insights
        
        # Test with empty data
        empty_insights = generate_similarity_insights(
            "NonExistent Player",
            [],
            ["goals"],
            False,
            {}
        )
        
        if "No insights available" in empty_insights:
            print("✅ Empty data case handled correctly")
        else:
            print("❌ Empty data case not handled properly")
            return False
        
        # Test with minimal data
        minimal_data = {
            "Player A": {
                "goals": 5,
                "team": "Team A",
                "position": "CF"
            }
        }
        
        minimal_insights = generate_similarity_insights(
            "Player A",
            [("Player A", 1.0)],
            ["goals"],
            False,
            minimal_data
        )
        
        if len(minimal_insights) > 50:  # Should still generate some content
            print("✅ Minimal data case handled correctly")
        else:
            print("❌ Minimal data case not handled properly")
            return False
        
        print("✅ All edge cases handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing edge cases: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("=" * 80)
    print("AI INSIGHTS FUNCTIONALITY VERIFICATION")
    print("=" * 80)
    print("Testing the new AI insights feature for Find Similar Player")
    print()
    
    # Test 1: Import test
    import_test_passed = test_ai_insights_import()
    
    # Test 2: Insights generation test
    generation_test_passed = test_ai_insights_generation()
    
    # Test 3: Content quality test
    quality_test_passed = test_insights_content_quality()
    
    # Test 4: Edge cases test
    edge_cases_test_passed = test_edge_cases()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = (import_test_passed and generation_test_passed and 
                       quality_test_passed and edge_cases_test_passed)
    
    if import_test_passed:
        print("✅ AI insights import: Working correctly")
    else:
        print("❌ AI insights import: Failed")
    
    if generation_test_passed:
        print("✅ Insights generation: Working correctly")
    else:
        print("❌ Insights generation: Failed")
    
    if quality_test_passed:
        print("✅ Content quality: Working correctly")
    else:
        print("❌ Content quality: Failed")
    
    if edge_cases_test_passed:
        print("✅ Edge cases: Working correctly")
    else:
        print("❌ Edge cases: Failed")
    
    print()
    
    if all_tests_passed:
        print("🎉 SUCCESS! AI insights functionality is working correctly.")
        print("\nFeatures implemented:")
        print("- ✅ Comprehensive similarity analysis")
        print("- ✅ Player profile comparisons")
        print("- ✅ Statistical attribute analysis")
        print("- ✅ Key insights and patterns")
        print("- ✅ Actionable recommendations")
        print("- ✅ Proper markdown formatting")
        print("- ✅ Per 90 minutes support")
        print("- ✅ Edge case handling")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Navigate to 'Find Similar Player' menu")
        print("3. Test the AI insights with real player data")
    else:
        print("💥 FAILED! Some AI insights tests did not pass.")
        print("\nPlease fix the issues above before proceeding.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
