import logging

from energy_logic import (
    calculate_energy_financials,
    show_devices,
    trigger_overload_alert,
    update_indices,
)

logger = logging.getLogger(__name__)

ERR_E05 = (
    "[Lỗi] (ERR-E05): Lựa chọn sai! Vui lòng nhập đúng số thứ tự chức năng từ 1 đến 5!"
)


def display_menu():
    """Display the main console menu."""
    print("\n" + "=" * 52)
    print("   SMART ENERGY MONITOR - PHÒNG CƠ ĐIỆN")
    print("=" * 52)
    print("1. Xem danh sách thiết bị giám sát")
    print("2. Cập nhật chỉ số điện tiêu thụ (Check-in)")
    print("3. Kích hoạt trạng thái cảnh báo quá tải")
    print("4. Tính tổng lượng điện & Chi phí năng lượng")
    print("5. Thoát chương trình")
    print("=" * 52)


def show_energy_financials(devices_list):
    """Calculate and display total electricity consumption and energy cost."""
    if not devices_list:
        print("Hệ thống hiện chưa có thiết bị giám sát nào!")
        return

    total_kwh, discount_percent, final_cost = calculate_energy_financials(
        devices_list
    )

    print("\n--- BÁO CÁO CHI PHÍ NĂNG LƯỢNG ---")
    print(f"Tổng lượng điện tiêu thụ: {total_kwh:,.0f} kWh")
    print(f"Chiết khấu áp dụng: {discount_percent:.0f}%")
    print(f"Tổng tiền sau chiết khấu: {final_cost:,.0f} VND")


def get_menu_choice():
    """Read and validate main menu choice from user input."""
    while True:
        try:
            choice = int(input("Mời chọn chức năng (1-5): "))
            if 1 <= choice <= 5:
                return choice
            print(ERR_E05)
            logger.error("[Lỗi]: Người dùng chọn số ngoài dải [1, 5]")
        except ValueError:
            print(ERR_E05)
            logger.error("[Lỗi]: Người dùng nhập ký tự không hợp lệ tại menu chính")


def main():
    """Main orchestration loop for Smart Energy Monitor."""
    devices_list = [
        {
            "id": "M01",
            "location": "Mechanical Shop A",
            "old_index": 10000,
            "new_index": 16000,
            "status": "Normal",
        },
        {
            "id": "M02",
            "location": "Electrical Shop B",
            "old_index": 25000,
            "new_index": 28000,
            "status": "Normal",
        },
        {
            "id": "M03",
            "location": "Assembly Line C",
            "old_index": 5000,
            "new_index": 8000,
            "status": "Normal",
        },
    ]

    logger.info("Smart Energy Monitor started")

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            show_devices(devices_list)

        elif choice == 2:
            if not devices_list:
                print("Hệ thống hiện chưa có thiết bị giám sát nào!")
            else:
                update_indices(devices_list)

        elif choice == 3:
            if not devices_list:
                print("Hệ thống hiện chưa có thiết bị giám sát nào!")
            else:
                trigger_overload_alert(devices_list)

        elif choice == 4:
            show_energy_financials(devices_list)

        elif choice == 5:
            logger.info("User exited Smart Energy Monitor")
            print("Đã thoát chương trình. Hẹn gặp lại!")
            break


if __name__ == "__main__":
    main()
