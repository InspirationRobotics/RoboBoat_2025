import smbus2
import time
"""
This is a simple test script for arduino PWM value
We don't need to continously send signals to arduino because I2C doesn't require that
"""
# Function to send PWM values to Arduino via I2C
def send_pwm_list(pwm_list, address=8, bus_num=1):
    bus = smbus2.SMBus(bus_num)
    data = []
    for value in pwm_list:
        data.extend([value >> 8, value & 0xFF])
    bus.write_i2c_block_data(address, 0, data)
    print(f"Sent: {pwm_list}")

# Main loop to take user input and send PWM list
if __name__ == "__main__":
    pwm_values = [1500, 1500, 1500, 1500]  # Initialize PWM values
    while True:
        print(f"Current PWM values: {pwm_values}")
        user_input = input("Enter new PWM values for forward_port, forward_starboard, aft_port, aft_starboard (comma-separated): ")
        try:
            new_values = [int(x) for x in user_input.split(",")]
            if len(new_values) == 4:
                pwm_values = new_values
                send_pwm_list(pwm_values)
            else:
                print("Error: Please enter exactly 4 values.")
        except ValueError:
            print("Error: Please enter valid integers.")
        time.sleep(1)
