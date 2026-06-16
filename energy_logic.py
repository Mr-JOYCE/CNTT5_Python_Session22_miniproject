import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

BASE_ELECTRICITY_RATE = 3000
DISCOUNT_THRESHOLD_KWH = 50000
DISCOUNT_PERCENT = 3.0
OVERLOAD_THRESHOLD_KWH = 5000

ERR_E01 = (
    "[Lỗi] (ERR-E01): Mã thiết bị này không tồn tại trong danh sách hệ thống!"
)
ERR_E02 = (
    "[Lỗi] (ERR-E02): Số liệu lỗi! Chỉ số mới không được nhỏ hơn chỉ số cũ!"
)
ERR_E03 = (
    "[Lỗi] (ERR-E03): Định dạng không hợp lệ! Chỉ số điện phải là số lớn hơn hoặc bằng 0!"
)
ERR_E04 = (
    "[Lỗi] (ERR-E04): Thao tác bị hủy! Thiết bị này đã được kích hoạt trạng thái OVERLOAD từ trước!"
)


def find_device(devices_list, device_id):
    """Return device dict matching device_id, or None if not found."""
    for device in devices_list:
        if device["id"] == device_id:
            return device
    return None


def show_devices(devices_list):
    """Display all monitoring devices in a formatted console table."""
    logger.debug(
        "Showing device list with %s records",
        len(devices_list),
    )

    if not devices_list:
        print("Hệ thống hiện chưa có thiết bị giám sát nào!")
        return

    header = (
        f"{'MÃ THIẾT BỊ':<12} | "
        f"{'VỊ TRÍ PHÂN XƯỞNG':<22} | "
        f"{'CHỈ SỐ CŨ':>12} | "
        f"{'CHỈ SỐ MỚI':>12} | "
        f"{'TRẠNG THÁI':<10}"
    )
    print(header)
    print("-" * len(header))

    for device in devices_list:
        print(
            f"{device['id']:<12} | "
            f"{device['location']:<22} | "
            f"{device['old_index']:>12} | "
            f"{device['new_index']:>12} | "
            f"{device['status']:<10}"
        )


def _read_non_negative_number(prompt):
    """Read a non-negative number from user input with validation loop."""
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print(ERR_E03)
                logger.error(
                    "[Lỗi]: Kỹ thuật viên nhập số âm tại ô chỉ số điện"
                )
                continue
            return value
        except ValueError:
            print(ERR_E03)
            logger.error(
                "[Lỗi]: Kỹ thuật viên nhập sai định dạng số tại ô chỉ số điện"
            )


def update_indices(devices_list):
    """Update electricity indices for a device after validating user input."""
    logger.debug(
        "Starting index update for %s devices",
        len(devices_list),
    )

    device_id = input("Nhập mã thiết bị cần cập nhật chỉ số: ").strip()

    if not device_id:
        print(ERR_E01)
        logger.error("[Lỗi]: Mã thiết bị để trống")
        return

    device = find_device(devices_list, device_id)
    if device is None:
        print(ERR_E01)
        logger.error("[Lỗi]: Không tìm thấy thiết bị %s", device_id)
        return

    old_index = _read_non_negative_number("Nhập chỉ số cũ: ")

    while True:
        new_index = _read_non_negative_number("Nhập chỉ số mới: ")
        if new_index < old_index:
            print(ERR_E02)
            logger.error(
                "[Lỗi]: Chỉ số mới %.2f nhỏ hơn chỉ số cũ %.2f",
                new_index,
                old_index,
            )
            continue
        break

    device["old_index"] = old_index
    device["new_index"] = new_index

    logger.info(
        "[Thành công]: Đã check-in số liệu cho thiết bị %s",
        device_id,
    )
    print(
        f"[Thành công]: Đã cập nhật chỉ số điện cho thiết bị {device_id}."
    )


def trigger_overload_alert(devices_list):
    """Activate overload warning status when consumption exceeds safe threshold."""
    logger.debug(
        "Checking overload alert for %s devices",
        len(devices_list),
    )

    device_id = input("Nhập mã thiết bị cần kiểm tra cảnh báo quá tải: ").strip()

    if not device_id:
        print(ERR_E01)
        logger.error("[Lỗi]: Mã thiết bị để trống")
        return

    device = find_device(devices_list, device_id)
    if device is None:
        print(ERR_E01)
        logger.error("[Lỗi]: Không tìm thấy thiết bị %s", device_id)
        return

    consumption = device["new_index"] - device["old_index"]

    if consumption <= OVERLOAD_THRESHOLD_KWH:
        print(
            f"Thiết bị {device_id} đang trong ngưỡng an toàn "
            f"({consumption:,.0f} kWh / ngưỡng {OVERLOAD_THRESHOLD_KWH:,} kWh)."
        )
        return

    if device["status"] == "Overload":
        print(ERR_E04)
        logger.error(
            "[Lỗi]: Thiết bị %s đã ở trạng thái OVERLOAD",
            device_id,
        )
        return

    device["status"] = "Overload"
    logger.warning(
        "[Cảnh báo]: Thiết bị %s đã vượt ngưỡng tiêu thụ an toàn, chuyển sang OVERLOAD!",
        device_id,
    )
    print(
        f"[Thành công]: Thiết bị {device_id} đã được chuyển sang trạng thái OVERLOAD."
    )


def calculate_energy_financials(devices_list):
    """
    Calculate total consumption, discount rate, and final cost.

    Returns:
        tuple: (tong_kwh_tieu_thu, phan_tram_chiet_khau, tong_tien_sau_chiet_khau)
    """
    logger.debug(
        "Đang tính toán chi phí năng lượng cho %s thiết bị",
        len(devices_list),
    )

    if not devices_list:
        return (0.0, 0.0, 0.0)

    total_kwh = sum(
        device["new_index"] - device["old_index"]
        for device in devices_list
    )

    base_cost = total_kwh * BASE_ELECTRICITY_RATE

    if total_kwh >= DISCOUNT_THRESHOLD_KWH:
        discount_percent = DISCOUNT_PERCENT
    else:
        discount_percent = 0.0

    final_cost = base_cost * (1 - discount_percent / 100)

    return (total_kwh, discount_percent, final_cost)
