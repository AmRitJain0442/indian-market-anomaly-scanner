from src.plotting.research_guide import GLOSSARY


def test_glossary_is_unique_and_uses_requested_punctuation_style():
    terms = [term for _, term, _ in GLOSSARY]
    prose = " ".join(value for row in GLOSSARY for value in row)

    assert len(terms) >= 30
    assert len(terms) == len(set(terms))
    assert "—" not in prose
    assert ";" not in prose
