import pytest
from app.services.ai.input_analyzer import input_analyzer

def test_classify_product():
    spec = input_analyzer.analyze("Analyze Samsung Galaxy S26 reviews")
    assert spec.category == "PRODUCT"
    assert "Samsung" in spec.target_entity or "Galaxy" in spec.target_entity
    assert spec.source_queries.news_query is not None

def test_classify_policy():
    spec = input_analyzer.analyze("Analyze public opinion about the new EV subsidy policy in India")
    assert spec.category == "POLICY"
    assert "India" in spec.location_scope
    assert "EV" in spec.target_entity or "policy" in spec.target_entity.lower()

def test_classify_url():
    spec = input_analyzer.analyze("Analyze this Reddit discussion: https://reddit.com/r/technology/comments/12345/samsung_s26")
    assert spec.category == "URL"
    assert spec.url_target is not None

def test_classify_topic():
    spec = input_analyzer.analyze("Analyze discussions about electric vehicles")
    assert spec.category == "TOPIC"
    assert len(spec.target_entity) > 0
