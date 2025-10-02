"""
電費計算相關函數模組
"""
import numpy as np
from typing import List, Tuple, Dict


# 費率常數
BASIC_FEE_NON_SUMMER = 173.2  # 非夏月基本電費 (元/千瓦)
BASIC_FEE_SUMMER = 236.2       # 夏月基本電費 (元/千瓦)
SUMMER_MONTHS = [6, 7, 8, 9]   # 夏月月份


def calculate_monthly_fee(capacity: float, demand: float, month: int) -> float:
    """
    計算單月基本電費

    Args:
        capacity: 契約容量 (千瓦)
        demand: 當月最高需量 (千瓦)
        month: 月份 (1-12)

    Returns:
        當月基本電費 (元)

    Raises:
        ValueError: 當輸入值不合理時
    """
    if capacity <= 0:
        raise ValueError("契約容量必須大於 0")
    if demand < 0:
        raise ValueError("需量不能為負數")
    if month < 1 or month > 12:
        raise ValueError("月份必須介於 1-12 之間")

    # 判斷費率
    basic_fee_rate = BASIC_FEE_SUMMER if month in SUMMER_MONTHS else BASIC_FEE_NON_SUMMER

    # 計算超出容量
    excess = demand - capacity

    if excess <= 0:
        # 未超過契約容量
        return capacity * basic_fee_rate
    else:
        # 超過契約容量：計算罰款
        allowed_10_percent = capacity * 0.10

        if excess <= allowed_10_percent:
            # 超出 10% 以內：2 倍費率
            return capacity * basic_fee_rate + excess * basic_fee_rate * 2
        else:
            # 超出 10% 以上：2 倍 + 3 倍費率
            return (capacity * basic_fee_rate +
                    allowed_10_percent * basic_fee_rate * 2 +
                    (excess - allowed_10_percent) * basic_fee_rate * 3)


def calculate_annual_fee(capacity: float, monthly_demands: List[float]) -> float:
    """
    計算年度基本電費總額

    Args:
        capacity: 契約容量 (千瓦)
        monthly_demands: 12個月的最高需量列表 (千瓦)

    Returns:
        年度基本電費總額 (元)

    Raises:
        ValueError: 當輸入不合理時
    """
    if len(monthly_demands) != 12:
        raise ValueError("必須提供 12 個月的需量資料")

    total_fee = 0
    for month_idx, demand in enumerate(monthly_demands):
        month = month_idx + 1
        total_fee += calculate_monthly_fee(capacity, demand, month)

    return total_fee


def calculate_waste_and_penalty(capacity: float, monthly_demands: List[float]) -> Tuple[float, float]:
    """
    計算年度浪費金額與罰款金額

    Args:
        capacity: 契約容量 (千瓦)
        monthly_demands: 12個月的最高需量列表 (千瓦)

    Returns:
        (浪費金額, 罰款金額) 的元組 (元)
    """
    waste_total = 0
    penalty_total = 0

    for month_idx, demand in enumerate(monthly_demands):
        month = month_idx + 1
        rate = BASIC_FEE_SUMMER if month in SUMMER_MONTHS else BASIC_FEE_NON_SUMMER
        excess = demand - capacity

        if excess <= 0:
            # 未用滿：計算浪費容量
            wasted_kw = capacity - demand
            waste_total += wasted_kw * rate
        else:
            # 超出契約容量：計算罰款
            allowed = capacity * 0.10
            if excess <= allowed:
                penalty_total += excess * rate * 2
            else:
                penalty_total += allowed * rate * 2 + (excess - allowed) * rate * 3

    return waste_total, penalty_total


def find_optimal_capacity(monthly_demands: List[float]) -> Tuple[int, float, Dict[str, float]]:
    """
    尋找最佳契約容量

    Args:
        monthly_demands: 12個月的最高需量列表 (千瓦)

    Returns:
        (最佳容量, 最低費用, 詳細資訊字典) 的元組
        詳細資訊包含: waste (浪費金額), penalty (罰款金額)

    Raises:
        ValueError: 當輸入不合理時
    """
    if len(monthly_demands) != 12:
        raise ValueError("必須提供 12 個月的需量資料")

    if any(d < 0 for d in monthly_demands):
        raise ValueError("需量不能為負數")

    # 計算搜尋範圍
    min_demand = max(1, int(min(monthly_demands) * 0.8))
    max_demand = int(max(monthly_demands) * 1.5)
    capacities = np.arange(min_demand, max_demand + 1)

    # 計算所有可能容量的費用
    fees = [calculate_annual_fee(cap, monthly_demands) for cap in capacities]

    # 找出最佳容量
    optimal_idx = np.argmin(fees)
    optimal_capacity = int(capacities[optimal_idx])
    optimal_fee = fees[optimal_idx]

    # 計算最佳容量下的浪費與罰款
    waste, penalty = calculate_waste_and_penalty(optimal_capacity, monthly_demands)

    return optimal_capacity, optimal_fee, {
        'waste': waste,
        'penalty': penalty
    }


def get_fee_distribution(monthly_demands: List[float]) -> Tuple[np.ndarray, List[float]]:
    """
    取得不同契約容量下的費用分布（用於繪圖）

    Args:
        monthly_demands: 12個月的最高需量列表

    Returns:
        (容量陣列, 費用列表) 的元組
    """
    min_demand = max(1, int(min(monthly_demands) * 0.8))
    max_demand = int(max(monthly_demands) * 1.5)
    capacities = np.arange(min_demand, max_demand + 1)
    fees = [calculate_annual_fee(cap, monthly_demands) for cap in capacities]

    return capacities, fees
