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