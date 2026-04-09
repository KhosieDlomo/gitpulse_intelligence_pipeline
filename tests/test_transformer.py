import pytest
from src.transformer import DataTransformer, LocalSummarizer

# 1. Test the AI Categorization Logic
def test_ai_label_categorization():
    transformer = DataTransformer()
    
    # Logic Test: Contains "api" and "http" -> Should be Web Dev
    web_data = transformer._ai_label("this is a new rest api built with http protocols")
    assert web_data == "Web Dev"
    
    # Logic Test: Contains "model" and "inference" -> Should be AI/ML
    ai_data = transformer._ai_label("a new model for fast inference")
    assert ai_data == "AI/ML"
    
    # Fallback Test: No keywords -> Should be General
    general_data = transformer._ai_label("some random text")
    assert general_data == "General"

# 2. Test the Summarizer Cleaning Logic
def test_summarizer_cleaning():
    summarizer = LocalSummarizer()
    
    # Test Markdown and HTML stripping
    dirty_text = "Check out this project! <img src='link'> [Read more](http://link) # Features * Speed"
    clean_summary = summarizer.summarize(dirty_text)
    
    # It should remove the tags and markdown characters
    assert "<img" not in clean_summary
    assert "Check out this project! Read more Features Speed" in clean_summary

# 3. Test the Full Process Function
def test_transformer_process():
    transformer = DataTransformer()
    raw_input = {
        "name": "TestRepo",
        "stargazers_count": 150,
        "html_url": "https://github.com/test",
        "description": "Vulkan based shader renderer"
    }
    
    processed = transformer.process(raw_input)
    
    assert processed["name"] == "TestRepo"
    assert processed["label"] == "3D/Graphics" 
    assert processed["stars"] == 150