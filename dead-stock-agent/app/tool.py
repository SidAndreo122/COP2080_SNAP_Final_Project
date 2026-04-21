# Dead Stock Detector
# tool.py
# -------------------------------------------------------
# Tool Name : Dead Stock Detector
# Domain : Supply Chain/Inventory
# Author : Sidney Andreano
# Description: This function computes the financial holding cost and severity of risk
# towards a dead stock scenario. This can be helpful to know what product is at risk of "running out" soon.
# Usage : See README.md for a sample call.
# -------------------------------------------------------
from enum import Enum
class Severity(Enum):
    HEALTHY = "healthy"
    SLOW = "slow-moving"
    RISK = "at risk"
    DEAD = "dead stock"

def get_severity(days):
    if days <= 30:
        return Severity.HEALTHY
    if days > 30 and days <= 90:
        return Severity.SLOW
    if days > 90 and days <= 180:
        return Severity.RISK
    return Severity.DEAD

def detect_dead_stock(units_on_hand: float, daily_demand: float, holding_cost_per_day: float, cost_per_unit: float) -> dict:
    """
        Computes the financial holding cost and severity classification of slow-moving or dead inventory.
        Args:
            units_on_hand (float): Amount of individual units of product that is currently available.
            daily_demand (float): A numerical representation of daily demand of a certain product.
            holding_cost_per_day (float): The cost amount per day of holding a product in inventory.
            cost_per_unit (float): The cost amount of a product per individual unit.
        Returns:
            dict: {
                "result": <total_holding_cost, holding_cost_per_day * units_on_hand * days_of_stock>,
                "unit": <"USD ($)">,
                "days_of_stock_remaining": <days_of_stock, units_on_hand / daily_demand>,
                "severity": <severity, label on how severe risk of dead stock is>,
                "detail": <a general summary of all previous dictionary keys>
            }
        Raises:
            ValueError: if any input is out of expected range or type.
    # --- Input Validation ---
        units_on_hand:
            This parameter is invalid if the value is negative.
        daily_demand:
            This parameter is invalid if the value is negative and the special case when demand
            is zero, meaning days_of_stock cannot be computed (days/0).
        holding_cost_per_day:
            This parameter is invalid if the value is negative and taking the assumption that
            the cost cannot be zero.
        cost_per_unit:
            This parameter is invalid if the value is negative and the product cannot be sold for free.
        
    # --- Core Logic ---
    """

    # Input Validation
    if units_on_hand < 0:
        raise ValueError(f"units_on_hand must be positive, got {units_on_hand}.")
    if daily_demand < 0:
        raise ValueError(f"daily_demand must be positive, got {daily_demand}.")
    if holding_cost_per_day <= 0:
        raise ValueError(f"holding_cost_per_day must be positive and must not be 0, got {holding_cost_per_day}.")
    if cost_per_unit <= 0:
        raise ValueError(f"cost_per_unit must be positive and must not be zero, got {cost_per_unit}.")
    if daily_demand == 0:
        return {
            "result": units_on_hand * holding_cost_per_day,
            "unit": "USD ($)",
            "days_of_stock_remaining": float('inf'),
            "severity": Severity.DEAD,
            "detail": f"{units_on_hand} units on hand with no demand. Classified as 'dead stock', costing ${units_on_hand * holding_cost_per_day:,.2f}/day in holding costs indefinitely."
        }
    

    days_of_stock = units_on_hand / daily_demand # days of stock remaining based on demand
    total_holding_cost = units_on_hand * holding_cost_per_day * days_of_stock # financial loss 
    severity = get_severity(days_of_stock) # severity label for levels of risk (risk of dead stock)
    return {
        "result": total_holding_cost,
        "unit": "USD ($)", 
        "days_of_stock_remaining": days_of_stock,
        "severity": severity,
        "detail": f"{units_on_hand} units on hand with {daily_demand} units/day demand represents {days_of_stock:.1f} days of stock, classified as '{severity.value}', costing ${total_holding_cost:,.2f} in holding costs."
        }

def detect_dead_stock_batch(skus: list[dict]) -> list[dict]:
        """
    Processes a list of SKUs through the dead stock detector and returns
    results sorted by total holding cost (highest financial risk first).
 
    Args:
        skus (list[dict]): Each dict must contain:
            - sku_id              (str)
            - product_name        (str)
            - units_on_hand       (float)
            - daily_demand        (float)
            - holding_cost_per_day(float)
            - cost_per_unit       (float)
 
        Optional keys passed through to output:
            - category (str)
 
    Returns:
        list[dict]: One result dict per SKU, sorted by holding cost descending.
        Each dict contains all input fields plus:
            - result                 (float) - total holding cost USD
            - unit                   (str)
            - days_of_stock_remaining(float)
            - severity               (Severity)
            - detail                 (str)
            - error                  (str | None) – set if processing failed
 
    Raises:
        TypeError:  if skus is not a list.
        ValueError: if skus is empty.
    """
    if not isinstance(skus, list):
        raise TypeError(f"skus must be a list, got {type(skus).__name__}.")
    if len(skus) == 0:
        raise ValueError("skus list must not be empty.")
    
    results = []
    for sku in skus:
        sku_id       = sku.get("sku_id", "UNKNOWN")
        product_name = sku.get("product_name", "Unknown Product")
        category     = sku.get("category", "Uncategorized")

        try:
            analysis = detect_dead_stock(
                units_on_hand        = float(sku["units_on_hand"]),
                daily_demand         = float(sku["daily_demand"]),
                holding_cost_per_day = float(sku["holding_cost_per_day"]),
                cost_per_unit        = float(sku["cost_per_unit"]),
            )
            results.append({
                "sku_id":       sku_id,
                "product_name": product_name,
                "category":     category,
                "error":        None,
                **analysis,
            })
 
        except (ValueError, KeyError, TypeError) as e:
            # Log the failure but continue processing remaining SKUs
            results.append({
                "sku_id":                  sku_id,
                "product_name":            product_name,
                "category":                category,
                "result":                  None,
                "unit":                    "USD ($)",
                "days_of_stock_remaining": None,
                "severity":                None,
                "detail":                  None,
                "error":                   str(e),
            })

        results.sort(
            key = lambda r: r["result"] if r["result"] is not None else -1,
            reverse = True,
        )

        return results