# utils/mode_selector.py

MODE_LICENCE = 1
MODE_HSRP = 2
MODE_COMBINED = 3


def select_mode(use_hardware=False):
    """
    Keyboard mode now
    GPIO button mode later
    """

    if not use_hardware:
        print("\nSelect Verification Mode:")
        print("1. Licence Verification Mode")
        print("2. HSRP Vehicle Verification Mode")
        print("3. Combined Mode")

        try:
            return int(input("Enter choice: "))
        except ValueError:
            return 0

    # Hardware GPIO logic will be added later
    return 0