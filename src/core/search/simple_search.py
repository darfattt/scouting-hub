import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..data_processor import GoalkeeperDataProcessor

class GoalkeeperSearch:
    """
    Simple search system for goalkeeper data using TF-IDF.
    """

    def __init__(
        self,
        data_dir: str = "data/stats",
        model_path: str = "tfidf_model.pkl"
    ):
        """
        Initialize the search system.

        Args:
            data_dir: Directory containing the goalkeeper statistics CSV files
            model_path: Path to save/load the TF-IDF model
        """
        self.data_dir = data_dir
        self.model_path = model_path

        # Initialize data processor
        self.data_processor = GoalkeeperDataProcessor(data_dir)

        # Initialize TF-IDF vectorizer
        self.vectorizer = None
        self.document_vectors = None
        self.documents = []

    def build_search_index(self, force_rebuild: bool = False) -> None:
        """
        Build the search index from the goalkeeper data.

        Args:
            force_rebuild: Whether to force rebuilding the index even if it exists
        """
        # Check if index already exists
        if os.path.exists(self.model_path) and not force_rebuild:
            print(f"Loading existing search index from {self.model_path}")
            with open(self.model_path, 'rb') as f:
                saved_data = pickle.load(f)
                self.vectorizer = saved_data['vectorizer']
                self.document_vectors = saved_data['document_vectors']
                self.documents = saved_data['documents']
            return

        print("Building search index from goalkeeper data...")

        # Process the data
        print("Processing goalkeeper data...")
        self.data_processor.process_data()

        # Get text representations for all players
        print("Creating text representations for players...")
        player_texts = self.data_processor.get_all_player_texts()
        print(f"Created text representations for {len(player_texts)} players")

        if not player_texts:
            print("No player data found.")
            return

        # Create documents for the search index
        print("Creating documents for search index...")
        self.documents = [
            {
                'content': item['content'],
                'player': item['player']
            }
            for item in player_texts
        ]

        # Create TF-IDF vectors
        print("Creating TF-IDF vectors...")
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.document_vectors = self.vectorizer.fit_transform([doc['content'] for doc in self.documents])
        print("TF-IDF vectors created successfully!")

        # Save the model
        print(f"Saving search index to {self.model_path}")
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'document_vectors': self.document_vectors,
                'documents': self.documents
            }, f)

        print(f"Search index built with {len(self.documents)} documents and saved to {self.model_path}")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for goalkeeper profiles matching the query.

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing player information and relevance score
        """
        if self.vectorizer is None:
            self.build_search_index()

        if self.vectorizer is None:
            return []

        # Vectorize the query
        query_vector = self.vectorizer.transform([query])

        # Calculate similarity scores
        similarity_scores = cosine_similarity(query_vector, self.document_vectors).flatten()

        # Get top k results
        top_indices = similarity_scores.argsort()[-top_k:][::-1]

        # Create result list
        results = []
        for idx in top_indices:
            results.append({
                'player': self.documents[idx]['player'],
                'content': self.documents[idx]['content'],
                'score': similarity_scores[idx]
            })

        return results

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
    search = GoalkeeperSearch()
    search.build_search_index(force_rebuild=True)

    # Test a query
    results = search.search("Who is the goalkeeper with the highest save percentage?")
    print("\nSearch Results:")
    for i, result in enumerate(results):
        print(f"Result {i+1}: {result['player']} (Score: {result['score']:.4f})")
        print(f"Excerpt: {result['content'][:200]}...\n")

    # Test player comparison
    if search.data_processor.player_data:
        players = list(search.data_processor.player_data.keys())
        if len(players) >= 2:
            comparison = search.compare_players(players[0], players[1])
            print(f"\nComparison between {players[0]} and {players[1]}:")
            for metric, values in comparison["metrics"].items():
                print(f"- {metric}: {values[0]} vs {values[1]}")
