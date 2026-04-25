# unit tests

################################################
# Non-LLM Tool Tests
################################################
import pytest
from app.tool import detect_dead_stock, detect_dead_stock_batch, Severity

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

# =================================================
# Dead stock batch tests
# =================================================
def make_sku(sku_id, units, demand, holding_cost = 0.10, cost_per_unit=5.0, category="Hardware"):
    return {
        "sku_id" : sku_id,
        "product_name": f"Product {sku_id}",
        "category": category,
        "units_on_hand": units,
        "daily_demand": demand,
        "holding_cost_per_day": holding_cost,
        "cost_per_unit": cost_per_unit,
    }

def test_batch_returns_all_rows():
    skus = [make_sku("SKU-001", 50, 2.0), make_sku("SKU-002", 200, 1.0)]
    results = detect_dead_stock_batch(skus)
    assert len(results) == 2

def test_batch_sorted_by_holding_cost_descending():
    skus = [make_sku("SKU-001", 50, 2.0, holding_cost=0.10), make_sku("SKU-002", 500, 1.0, holding_cost=0.50)]
    results = detect_dead_stock_batch(skus)
    assert results[0]["sku_id"] == "SKU-002"
    assert results[0]["result"] >= results[1]["result"]

def test_batch_correct_severity_per_sku():
    """Each SKU should receive the correct severity classification."""
    skus = [
        make_sku("SKU-H", 30,  1.0),    
        make_sku("SKU-S", 60,  1.0),    
        make_sku("SKU-R", 150, 1.0),    
        make_sku("SKU-D", 500, 1.0),    
    ]
    results = detect_dead_stock_batch(skus)
    severity_map = {r["sku_id"]: r["severity"] for r in results}
    assert severity_map["SKU-H"] == Severity.HEALTHY
    assert severity_map["SKU-S"] == Severity.SLOW
    assert severity_map["SKU-R"] == Severity.RISK
    assert severity_map["SKU-D"] == Severity.DEAD

def test_batch_zero_demand_sku_classified_dead():
    """A SKU with zero demand should be classified as dead stock."""
    skus = [make_sku("SKU-001", 100, 0.0)]
    results = detect_dead_stock_batch(skus)
    assert results[0]["severity"] == Severity.DEAD
    assert results[0]["days_of_stock_remaining"] == float("inf")
 
# --- Error Handling ---
 
def test_batch_bad_row_does_not_crash():
    """A single invalid SKU should not stop the rest from processing."""
    skus = [
        make_sku("SKU-BAD", -999, 1.0),   # invalid units → ValueError inside
        make_sku("SKU-OK",   50,  2.0),
    ]
    results = detect_dead_stock_batch(skus)
    assert len(results) == 2
 
    bad = next(r for r in results if r["sku_id"] == "SKU-BAD")
    good = next(r for r in results if r["sku_id"] == "SKU-OK")
 
    assert bad["error"] is not None     # error captured on bad row
    assert good["error"] is None        # good row still processed correctly
 
def test_batch_missing_key_does_not_crash():
    """A SKU missing a required field should fail gracefully."""
    skus = [{"sku_id": "SKU-MISSING", "product_name": "No Data"}]  # missing all numeric fields
    results = detect_dead_stock_batch(skus)
    assert results[0]["error"] is not None
 
def test_batch_all_bad_rows_returns_all_errors():
    """Even if every row is invalid, all rows should be returned with errors."""
    skus = [
        make_sku("SKU-001", -1, 1.0),
        make_sku("SKU-002", -1, 1.0),
    ]
    results = detect_dead_stock_batch(skus)
    assert len(results) == 2
    assert all(r["error"] is not None for r in results)
 
# --- Input Validation ---
 
def test_batch_empty_list_raises():
    """An empty list should raise a ValueError."""
    with pytest.raises(ValueError):
        detect_dead_stock_batch([])
 
def test_batch_non_list_raises():
    """Passing a non-list should raise a TypeError."""
    with pytest.raises(TypeError):
        detect_dead_stock_batch("not a list")