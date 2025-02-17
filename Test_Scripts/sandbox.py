"""
Sandbox file to make it convenient to see how code works/experiment with syntax.
"""

tuple = (None, None)

if tuple == None:
    print("None")
else:
    print(tuple)

# import threading
# import time
# import queue

# # Function for the printing thread
# def print_thread(print_queue, print_rate, stop_event):
#     while not stop_event.is_set():
#         try:
#             # Get the value from the queue and print it
#             value = print_queue.get(timeout=print_rate)
#             print(f"Received value: {value}")
#         except queue.Empty:
#             # No value in the queue to print, can add any "idle" action here if needed
#             print("No value received.")
#             continue

# # Function for the sending thread
# def send_thread(send_queue, send_rate, stop_event):
#     count = 0
#     while not stop_event.is_set():
#         count += 1
#         send_queue.put(count)
#         print(f"Sent value: {count}")
#         time.sleep(send_rate)

# # Main function to setup and control the threads
# def main(send_rate, print_rate, duration):
#     send_queue = queue.Queue()
#     stop_event = threading.Event()

#     # Setup the printing thread
#     print_thread_instance = threading.Thread(target=print_thread, args=(send_queue, print_rate, stop_event))
#     print_thread_instance.daemon = True  # Ensure this thread exits when main program exits
#     print_thread_instance.start()

#     # Setup the sending thread
#     send_thread_instance = threading.Thread(target=send_thread, args=(send_queue, send_rate, stop_event))
#     send_thread_instance.daemon = True  # Ensure this thread exits when main program exits
#     send_thread_instance.start()

#     # Run for the specified duration
#     time.sleep(duration)
    
#     # Stop the sending thread
#     stop_event.set()

#     # Wait for threads to complete (optional)
#     send_thread_instance.join()
#     print_thread_instance.join()

# if __name__ == "__main__":
#     pos = {"1" : (64, 6), "2" : None}
#     pos["1"][0]
#     print(pos["1"][0], pos["1"][1])

#     # # Example configuration
#     # send_rate = 1  # Send a value every 1 second
#     # print_rate = 0.5  # Print a value every 2 seconds
#     # duration = 10  # Run for 10 seconds

#     # try:
#     #     main(send_rate, print_rate, duration)
#     # except KeyboardInterrupt:
#     #     main(0, 0, 0)

