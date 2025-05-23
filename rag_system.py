import os
from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from data_processor import GoalkeeperDataProcessor, OutfieldDataProcessor

class GoalkeeperRAG:
    """
    Retrieval-Augmented Generation system for goalkeeper data.
    """

    def __init__(
        self,
        model_name: str = "deepseek-r1:8b",
        embeddings_model_name: str = "deepseek-r1:8b",
        data_dir: str = "data/stats",
        vector_store_path: str = "vector_store"
    ):
        """
        Initialize the RAG system.

        Args:
            model_name: Name of the Ollama model to use for generation
            embeddings_model_name: Name of the Ollama model to use for embeddings
            data_dir: Directory containing the goalkeeper statistics CSV files
            vector_store_path: Path to save/load the vector store
        """
        self.model_name = model_name
        self.embeddings_model_name = embeddings_model_name
        self.data_dir = data_dir
        self.vector_store_path = vector_store_path

        # Initialize data processor
        self.data_processor = GoalkeeperDataProcessor(data_dir)

        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(model=embeddings_model_name)

        # Initialize LLM
        self.llm = OllamaLLM(model=model_name)

        # Initialize vector store
        self.vector_store = None

    def build_vector_store(self, force_rebuild: bool = False) -> None:
        """
        Build the vector store from the goalkeeper data.

        Args:
            force_rebuild: Whether to force rebuilding the vector store even if it exists
        """
        # Check if vector store already exists
        if os.path.exists(self.vector_store_path) and not force_rebuild:
            print(f"Loading existing vector store from {self.vector_store_path}")
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True  # Safe since we created this file ourselves
            )
            return

        print("Building vector store from goalkeeper data...")

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

        # Convert to documents for the vector store
        print("Converting to documents for vector store...")
        documents = [
            Document(
                page_content=item['content'],
                metadata={'player': item['player']}
            )
            for item in player_texts
        ]

        # Create the vector store
        print("Creating vector store with FAISS...")
        print("This may take some time as it needs to generate embeddings for all documents...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        print("Vector store created successfully!")

        # Save the vector store
        dirname = os.path.dirname(self.vector_store_path)
        if dirname:  # Only create directories if there's a directory component
            os.makedirs(dirname, exist_ok=True)
        self.vector_store.save_local(self.vector_store_path)

        print(f"Vector store built with {len(documents)} documents and saved to {self.vector_store_path}")

    def setup_retrieval_qa(self) -> RetrievalQA:
        """
        Set up the retrieval QA chain.

        Returns:
            RetrievalQA chain
        """
        if self.vector_store is None:
            self.build_vector_store()

        if self.vector_store is None:
            raise ValueError("Vector store could not be built or loaded.")

        # Create a retriever
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # Create a custom prompt template
        template = """
        You are a football/soccer goalkeeper scout and analyst. Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context:
        {context}

        Question: {question}

        Answer:
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # Create the retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        return qa_chain

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system.

        Args:
            question: Question to ask about goalkeepers

        Returns:
            Dictionary containing the answer and source documents
        """
        qa_chain = self.setup_retrieval_qa()
        result = qa_chain({"query": question})

        return {
            "answer": result["result"],
            "source_documents": result["source_documents"]
        }

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


class OutfieldRAG:
    """
    Base Retrieval-Augmented Generation system for outfield player data.
    Can be used for all outfield positions or filtered by specific position.
    """

    def __init__(
        self,
        model_name: str = "deepseek-r1:8b",
        embeddings_model_name: str = "deepseek-r1:8b",
        data_dir: str = "data/stats",
        vector_store_path: str = "vector_store_outfield",
        position_filter: str = None
    ):
        """
        Initialize the RAG system.

        Args:
            model_name: Name of the Ollama model to use for generation
            embeddings_model_name: Name of the Ollama model to use for embeddings
            data_dir: Directory containing the player statistics CSV files
            vector_store_path: Path to save/load the vector store
            position_filter: Filter by specific position (e.g., 'Forward', 'Midfielder', 'Defender')
        """
        self.model_name = model_name
        self.embeddings_model_name = embeddings_model_name
        self.data_dir = data_dir
        self.vector_store_path = vector_store_path
        self.position_filter = position_filter

        # Initialize data processor
        self.data_processor = OutfieldDataProcessor(data_dir, position_filter)

        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(model=embeddings_model_name)

        # Initialize LLM
        self.llm = OllamaLLM(model=model_name)

        # Initialize vector store
        self.vector_store = None

    def build_vector_store(self, force_rebuild: bool = False) -> None:
        """
        Build the vector store from the outfield player data.

        Args:
            force_rebuild: Whether to force rebuilding the vector store even if it exists
        """
        # Check if vector store already exists
        if os.path.exists(self.vector_store_path) and not force_rebuild:
            print(f"Loading existing vector store from {self.vector_store_path}")
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return

        position_text = f" ({self.position_filter})" if self.position_filter else ""
        print(f"Building vector store from outfield player data{position_text}...")

        # Process the data
        print("Processing outfield player data...")
        self.data_processor.process_data()

        # Get text representations for all players
        print("Creating text representations for players...")
        player_texts = self.data_processor.get_all_player_texts()
        print(f"Created text representations for {len(player_texts)} players")

        if not player_texts:
            print("No player data found.")
            return

        # Convert to documents for the vector store
        print("Converting to documents for vector store...")
        documents = [
            Document(
                page_content=item['content'],
                metadata={'player': item['player']}
            )
            for item in player_texts
        ]

        # Create the vector store
        print("Creating vector store with FAISS...")
        print("This may take some time as it needs to generate embeddings for all documents...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        print("Vector store created successfully!")

        # Save the vector store
        dirname = os.path.dirname(self.vector_store_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self.vector_store.save_local(self.vector_store_path)

        print(f"Vector store built with {len(documents)} documents and saved to {self.vector_store_path}")

    def setup_retrieval_qa(self) -> RetrievalQA:
        """
        Set up the retrieval QA chain.

        Returns:
            RetrievalQA chain
        """
        if self.vector_store is None:
            self.build_vector_store()

        if self.vector_store is None:
            raise ValueError("Vector store could not be built or loaded.")

        # Create a retriever
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # Create a custom prompt template based on position
        position_context = ""
        if self.position_filter:
            position_context = f"You are specifically analyzing {self.position_filter.lower()} players. "

        template = f"""
        You are a football/soccer scout and analyst. {position_context}Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context:
        {{context}}

        Question: {{question}}

        Answer:
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # Create the retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        return qa_chain

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system.

        Args:
            question: Question to ask about players

        Returns:
            Dictionary containing the answer and source documents
        """
        qa_chain = self.setup_retrieval_qa()
        result = qa_chain({"query": question})

        return {
            "answer": result["result"],
            "source_documents": result["source_documents"]
        }

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
                "goals": [stats1["goals"], stats2["goals"]],
                "assists": [stats1["assists"], stats2["assists"]],
                "goals_per_90": [stats1["goals_per_90"], stats2["goals_per_90"]],
                "assists_per_90": [stats1["assists_per_90"], stats2["assists_per_90"]],
                "pass_accuracy": [stats1["pass_accuracy"], stats2["pass_accuracy"]],
                "dribble_success_rate": [stats1["dribble_success_rate"], stats2["dribble_success_rate"]],
                "duel_success_rate": [stats1["duel_success_rate"], stats2["duel_success_rate"]]
            }
        }

        return comparison


class ForwardRAG(OutfieldRAG):
    """
    Specialized RAG system for forward players.
    """

    def __init__(
        self,
        model_name: str = "deepseek-r1:8b",
        embeddings_model_name: str = "deepseek-r1:8b",
        data_dir: str = "data/stats",
        vector_store_path: str = "vector_store_forwards"
    ):
        super().__init__(
            model_name=model_name,
            embeddings_model_name=embeddings_model_name,
            data_dir=data_dir,
            vector_store_path=vector_store_path,
            position_filter="Forward"
        )


class MidfielderRAG(OutfieldRAG):
    """
    Specialized RAG system for midfielder players.
    """

    def __init__(
        self,
        model_name: str = "deepseek-r1:8b",
        embeddings_model_name: str = "deepseek-r1:8b",
        data_dir: str = "data/stats",
        vector_store_path: str = "vector_store_midfielders"
    ):
        super().__init__(
            model_name=model_name,
            embeddings_model_name=embeddings_model_name,
            data_dir=data_dir,
            vector_store_path=vector_store_path,
            position_filter="Midfielder"
        )


class DefenderRAG(OutfieldRAG):
    """
    Specialized RAG system for defender players.
    """

    def __init__(
        self,
        model_name: str = "deepseek-r1:8b",
        embeddings_model_name: str = "deepseek-r1:8b",
        data_dir: str = "data/stats",
        vector_store_path: str = "vector_store_defenders"
    ):
        super().__init__(
            model_name=model_name,
            embeddings_model_name=embeddings_model_name,
            data_dir=data_dir,
            vector_store_path=vector_store_path,
            position_filter="Defender"
        )


if __name__ == "__main__":
    # Test the RAG systems
    print("Testing GoalkeeperRAG...")
    gk_rag = GoalkeeperRAG()
    gk_rag.build_vector_store(force_rebuild=True)

    # Test a query
    result = gk_rag.query("Who is the goalkeeper with the highest save percentage?")
    print(f"GK Answer: {result['answer']}")

    print("\nTesting ForwardRAG...")
    forward_rag = ForwardRAG()
    forward_rag.build_vector_store(force_rebuild=True)

    # Test a query
    result = forward_rag.query("Who is the forward with the most goals?")
    print(f"Forward Answer: {result['answer']}")

    print("\nTesting MidfielderRAG...")
    midfielder_rag = MidfielderRAG()
    midfielder_rag.build_vector_store(force_rebuild=True)

    # Test a query
    result = midfielder_rag.query("Who is the midfielder with the most assists?")
    print(f"Midfielder Answer: {result['answer']}")

    print("\nTesting DefenderRAG...")
    defender_rag = DefenderRAG()
    defender_rag.build_vector_store(force_rebuild=True)

    # Test a query
    result = defender_rag.query("Who is the defender with the most interceptions?")
    print(f"Defender Answer: {result['answer']}")
