try:
    import sklearn
    print(f"scikit-learn is installed. Version: {sklearn.__version__}")
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    print("TfidfVectorizer is available.")
    
    vectorizer = TfidfVectorizer()
    print("TfidfVectorizer can be instantiated.")
    
    print("All checks passed!")
except ImportError as e:
    print(f"Error importing scikit-learn: {e}")
except Exception as e:
    print(f"Error: {e}")
