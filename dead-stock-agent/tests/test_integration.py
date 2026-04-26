# requires api keys
# tests integration CSV -> agent -> respone
import pandas as pd
import pytest
from app.tool import detect_dead_stock_batch
from app.agent import create_agent, set_inventory_df, run_agent

@pytest.fixture(scope="module")
def sample_df():
    return pd.DataFrame([
        {"sku_id": "SKU-001", "product_name": "Bolt Set", "category": "Hardware",
         "units_on_hand": 500, "daily_demand": 0.0,
         "holding_cost_per_day": 0.15, "cost_per_unit": 12.50},
        {"sku_id": "SKU-002", "product_name": "Bubble Wrap", "category": "Packaging",
         "units_on_hand": 100, "daily_demand": 5.0,
         "holding_cost_per_day": 0.05, "cost_per_unit": 3.00},
    ])

def test_integration_pipeline(sample_df):
    """CSV-> tool -> agent -> response"""

    skus = sample_df.to_dict(orient="records")
    tool_results = detect_dead_stock_batch(skus)
    assert len(tool_results) == 2
    assert tool_results[0]["severity"] is not None

    set_inventory_df(sample_df)
    agent = create_agent()
    response = run_agent("Which products are dead stock and what should I do?", agent)

    assert isinstance(response, str)
    assert len(response) > 50 # not empty answer