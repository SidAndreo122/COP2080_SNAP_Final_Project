# load tests
# test if the tool can handle multiple requests
import concurrent.futures
from app.tool import detect_dead_stock

SAMPLE = {"units_on_han"}