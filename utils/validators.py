"""
輸入驗證模組
"""
from typing import List, Tuple, Optional


class ValidationError(Exception):
    """驗證錯誤例外"""
    pass


def validate_capacity(capacity: float) -> Tuple[bool, Optional[str]]:
    """
    驗證契約容量輸入

    Args:
        capacity: 契約容量 (千瓦)

    Returns:
        (是否有效, 錯誤訊息)
    """
    if capacity <= 0:
        return False, "契約容量必須大於 0"

    if capacity > 10000:
        return False, "契約容量過大 (超過 10,000 kW)，請確認輸入是否正確"

    return True, None


def validate_demand(demand: float, month: int) -> Tuple[bool, Optional[str]]:
    """
    驗證需量輸入

    Args:
        demand: 需量 (千瓦)
        month: 月份 (1-12)

    Returns:
        (是否有效, 錯誤訊息)
    """
    if demand < 0:
        return False, f"{month}月需量不能為負數"

    if demand > 10000:
        return False, f"{month}月需量過大 (超過 10,000 kW)，請確認輸入是否正確"

    return True, None


def validate_monthly_demands(monthly_demands: List[float]) -> Tuple[bool, Optional[str]]:
    """
    驗證 12 個月的需量資料

    Args:
        monthly_demands: 12個月的需量列表

    Returns:
        (是否有效, 錯誤訊息)
    """
    if len(monthly_demands) != 12:
        return False, f"必須提供 12 個月的資料，目前只有 {len(monthly_demands)} 個月"

    for i, demand in enumerate(monthly_demands):
        month = i + 1
        is_valid, error_msg = validate_demand(demand, month)
        if not is_valid:
            return False, error_msg

    return True, None


def validate_demand_vs_capacity(
    monthly_demands: List[float],
    capacity: float,
    warning_threshold: float = 2.0
) -> Tuple[bool, Optional[str], List[str]]:
    """
    驗證需量與契約容量的合理性

    Args:
        monthly_demands: 12個月的需量列表
        capacity: 契約容量
        warning_threshold: 警告閾值倍數

    Returns:
        (是否有效, 錯誤訊息, 警告訊息列表)
    """
    warnings = []

    # 檢查是否有月份的需量遠超過契約容量
    for i, demand in enumerate(monthly_demands):
        month = i + 1
        if demand > capacity * warning_threshold:
            warnings.append(
                f"⚠️ {month}月需量 ({demand:.1f} kW) 超過契約容量 {warning_threshold} 倍，"
                f"將產生高額罰款，建議重新確認輸入是否正確"
            )

    # 檢查是否所有月份的需量都遠低於契約容量
    max_demand = max(monthly_demands)
    if max_demand < capacity * 0.5:
        warnings.append(
            f"ℹ️ 所有月份需量都低於契約容量的 50%，"
            f"建議可考慮調降契約容量以節省基本電費"
        )

    # 檢查需量變化是否過大
    min_demand = min(monthly_demands)
    if max_demand > 0 and min_demand > 0 and (max_demand / min_demand) > 3:
        warnings.append(
            f"ℹ️ 最高需量 ({max_demand:.1f} kW) 與最低需量 ({min_demand:.1f} kW) "
            f"差異較大，可能是夏季與非夏季用電差異所致"
        )

    return True, None, warnings


def get_reasonable_capacity_range(monthly_demands: List[float]) -> Tuple[int, int]:
    """
    根據需量資料建議合理的契約容量範圍

    Args:
        monthly_demands: 12個月的需量列表

    Returns:
        (建議最小容量, 建議最大容量)
    """
    max_demand = max(monthly_demands)
    min_demand = min(monthly_demands)

    # 建議範圍：最高需量的 0.8 ~ 1.3 倍
    suggested_min = max(1, int(max_demand * 0.8))
    suggested_max = int(max_demand * 1.3)

    return suggested_min, suggested_max


def format_validation_messages(warnings: List[str]) -> str:
    """
    格式化驗證警告訊息

    Args:
        warnings: 警告訊息列表

    Returns:
        格式化後的字串
    """
    if not warnings:
        return ""

    return "\n\n".join(warnings)
