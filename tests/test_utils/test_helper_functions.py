from src.utils import parse_weight

def test_parse_weight():
    assert parse_weight("1000 g") == 1000
