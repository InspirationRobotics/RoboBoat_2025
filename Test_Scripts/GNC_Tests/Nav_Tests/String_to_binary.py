def main():
    # Prompt for 4 comma-separated integers
    user_input = input("Enter 4 comma-separated numbers (e.g. '1500, 1500, 1500, 1500'): ")

    # Split and convert each part to an integer
    values = [int(part.strip()) for part in user_input.split(",")]

    # Create a list of binary strings (without the '0b' prefix)
    binary_strings = [bin(val)[2:] for val in values]

    # Print them on one line, separated by commas
    print("Decoded binary values:")
    print(",".join(binary_strings))

if __name__ == "__main__":
    main()
