def get_gesture_input():
    """
    Simulated gesture input.
    In real system: camera / CV model output
    """
    print("Choose a gesture:")
    print("1 - Open Palm")
    print("2 - Fist")
    print("3 - Pointing")

    choice = input("Enter choice: ")

    return choice