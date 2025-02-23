"""
Sandbox file to make it convenient to see how code works/experiment with syntax.
"""
# import time
# from GNC.Guidance_Core import mission_helper

# start_time = time.time()
# m = mission_helper.MissionHelper()
# data = m.load_json(r"GNC/Guidance_Core/Config/barco_polo.json")
# m.parse_config_data(data)
# print(m.mission_sequence)

import math

x, y = (0, 10)
vector_distance = round(math.sqrt(x^2 + y^2), 2)
vector_theta = round(math.degrees(math.atan2(y, (x + 0.001))), 2)
print(vector_theta)

# def experiment(*, box):
#     if box is not None and box == 1:
#         print("1")
#     else:
#         print("None")

# experiment()

# tr = False
# start_time = time.time()

# while True:
#     list = [0, 0, 0, 0]

#     if time.time() - start_time < 5:
#         tr = False
#     else:
#         tr = True

#     if tr:
#         list = [1, 1, 1, 1]
#     else:
#         list = [2, 2, 2, 2]

#     print(list)
#     time.sleep(1)


# from GNC.Nav_Core import gis_funcs

# lat1, lon1 = (32.92346104343789, -117.03798665283499)
# lat2, lon2 = (32.92344454248662, -117.03792796294756)


# print(gis_funcs.bearing(lat1, lon1, lat2, lon2))

# tuple = (None, None)

# if tuple == None:
#     print("None")
# else:
#     print(tuple)

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

