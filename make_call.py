import sys

from app import TARGET_NUMBER, place_call

if __name__ == "__main__":
    to_number = sys.argv[1] if len(sys.argv) > 1 else TARGET_NUMBER
    try:
        uuid = place_call(to_number)
        print(f"Call initiated to {to_number}. Request UUID: {uuid}")
    except Exception as e:
        print(f"Failed to place call: {e}")
        sys.exit(1)
