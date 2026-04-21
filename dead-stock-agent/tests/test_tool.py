# unit tests

################################################
# Non-LLM Tool Tests
################################################
import pytest
from dead-stock-agent/app/tool import detect_dead_stock, Severity

def test_happy_path():
    result = detect_dead_stock(100, 5, 2.0, 10.0)
    assert result["result"] == 4000.0
    assert result["severity"] == Severity.HEALTHY
    assert result["unit"] == "USD ($)"

def test_zero_demand():
    result = detect_dead_stock(100, 0, 2.0, 10.0)
    assert result["days_of_stock_remaining"] == float('inf')
    assert result["severity"] == Severity.DEAD

def test_invalid_input_raises():
    with pytest.raises(ValueError):
        detect_dead_stock(-100, 5, 2.0, 10.0)