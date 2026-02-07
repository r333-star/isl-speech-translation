from backend.gesture_input import get_gesture_input
from backend.isl_translator import translate_gesture

def main():
    gesture = get_gesture_input()
    result = translate_gesture(gesture)

    print("\nTranslated Text:")
    print(result)

if __name__ == "__main__":
    main()