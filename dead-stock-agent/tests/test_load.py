# load tests
# test if the tool can handle multiple requests
import concurrent.futures
from app.tool import detect_dead_stock

SAMPLE = {"units_on_hand": 200, "daily_demand": 2.0, "holding_cost_per_day": 0.15, "cost_per_unit": 10.0}

def single_call(_):
    return detect_dead_stock(**SAMPLE)

def test_load_multiple_requests():
    """Simulates 20 requests to the tool"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(single_call, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 20
    assert all(r["severity"] is not None for r in results)