import os
import pickle
from typing import List, Dict, Any, Optional
from data_processor import GoalkeeperDataProcessor

class SimpleGoalkeeperSearch:
    """
    Very simple search system for goalkeeper data using basic string matching.
    """
    
    def __init__(
        self, 
        data_dir: str = "data/stats",
        cache_path: str = "player_data.pkl"
    ):
        """
        Initialize the search system.
        
        Args:
            data_dir: Directory containing the goalkeeper statistics CSV files
            cache_path: Path to save/load the processed player data
        """
        self.data_dir = data_dir
        self.cache_path = cache_path
        
        # Initialize data processor
        self.data_processor = GoalkeeperDataProcessor(data_dir)
        self.documents = []
        
    def build_search_index(self, force_rebuild: bool = False) -> None:
        """
        Build the search index from the goalkeeper data.
        
        Args:
            force_rebuild: Whether to force rebuilding the index even if it exists
        """
        # Check if cache already exists
        if os.path.exists(self.cache_path) and not force_rebuild:
            print(f"Loading existing player data from {self.cache_path}")
            with open(self.cache_path, 'rb') as f:
                saved_data = pickle.load(f)
                self.data_processor.player_data = saved_data['player_data']
                self.documents = saved_data['documents']
            return
            
        print("Processing goalkeeper data...")
        
        # Process the data
        self.data_processor.process_data()
        
        # Get text representations for all players
        print("Creating text representations for players...")
        player_texts = self.data_processor.get_all_player_texts()
        print(f"Created text representations for {len(player_texts)} players")
        
        if not player_texts:
            print("No player data found.")
            return
            
        # Create documents for the search index
        print("Creating documents for search...")
        self.documents = [
            {
                'content': item['content'],
                'player': item['player']
            }
            for item in player_texts
        ]
        
        # Save the processed data
        print(f"Saving player data to {self.cache_path}")
        with open(self.cache_path, 'wb') as f:
            pickle.dump({
                'player_data': self.data_processor.player_data,
                'documents': self.documents
            }, f)
        
        print(f"Player data processed for {len(self.documents)} players and saved to {self.cache_path}")
        
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for goalkeeper profiles matching the query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing player information and relevance score
        """
        if not self.documents:
            self.build_search_index()
            
        if not self.documents:
            return []
            
        # Simple search by counting query terms in each document
        query_terms = query.lower().split()
        results = []
        
        for doc in self.documents:
            content = doc['content'].lower()
            score = sum(content.count(term) for term in query_terms)
            
            if score > 0:
                results.append({
                    'player': doc['player'],
                    'content': doc['content'],
                    'score': score
                })
        
        # Sort by score and take top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
        
    def get_player_stats(self, player_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Dictionary containing player statistics or None if player not found
        """
        if not self.data_processor.player_data:
            self.data_processor.process_data()
            
        return self.data_processor.player_data.get(player_name)
        
    def compare_players(self, player1: str, player2: str) -> Dict[str, Any]:
        """
        Compare two players based on their statistics.
        
        Args:
            player1: Name of the first player
            player2: Name of the second player
            
        Returns:
            Dictionary containing comparison results
        """
        stats1 = self.get_player_stats(player1)
        stats2 = self.get_player_stats(player2)
        
        if not stats1 or not stats2:
            return {"error": "One or both players not found"}
            
        # Create comparison
        comparison = {
            "players": [player1, player2],
            "metrics": {
                "matches": [stats1["matches"], stats2["matches"]],
                "minutes": [stats1["minutes"], stats2["minutes"]],
                "conceded_goals": [stats1["conceded_goals"], stats2["conceded_goals"]],
                "saves": [stats1["saves"], stats2["saves"]],
                "shots_against": [stats1["shots_against"], stats2["shots_against"]],
                "save_percentage": [stats1["save_percentage"], stats2["save_percentage"]],
                "goals_conceded_per_90": [stats1["goals_conceded_per_90"], stats2["goals_conceded_per_90"]]
            }
        }
        
        return comparison

if __name__ == "__main__":
    # Test the search system
    search = SimpleGoalkeeperSearch()
    search.build_search_index(force_rebuild=True)
    
    # Test a query
    results = search.search("high save percentage")
    print("\nSearch Results:")
    for i, result in enumerate(results):
        print(f"Result {i+1}: {result['player']} (Score: {result['score']})")
        print(f"Excerpt: {result['content'][:200]}...\n")
    
    # Test player comparison
    if search.data_processor.player_data:
        players = list(search.data_processor.player_data.keys())
        if len(players) >= 2:
            comparison = search.compare_players(players[0], players[1])
            print(f"\nComparison between {players[0]} and {players[1]}:")
            for metric, values in comparison["metrics"].items():
                print(f"- {metric}: {values[0]} vs {values[1]}")
