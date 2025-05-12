...
            white_centroids, white_info = find_contours(mask_white, frame, 'white')

            match = find_closest_match(black_info, white_centroids)
            if match:
                closest_black, closest_w, closest_h, bbox_x, bbox_y = match
                x, y = closest_black
                
                bbox_x2 = bbox_x + closest_w
                bbox_y2 = bbox_y + closest_h
                roi_disparity = disparity_map[bbox_y:bbox_y2, bbox_x:bbox_x2].astype(np.float32)

                if roi_disparity.size > 0:
                    mean_disparity = np.mean(roi_disparity) / 16.0  # subpixel mode
                    if mean_disparity > 0:
                        baseline_m = 0.075
                        focal_length_px = 870  # Example, replace with calibration
                        distance_m = (focal_length_px * baseline_m) / mean_disparity

                        if motor_move:
                            motor.surge(0.5)

                        cv2.circle(frame, (x, y), 15, (0, 0, 255), 3)
                        cv2.putText(frame, f'{closest_w}x{closest_h}px, {distance_m:.2f}m',
                                    (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                        if ball_launched and distance_m <= LAUNCH_DISTANCE_THRESHOLD and time.time() - last_shot_time >= TIME_DELAY:
                            if motor_move:
                                motor.stay()
                            launch_ardiuno(ardiuno_compound)
                            print("Ball launched!")
                            last_shot_time = time.time()
                            ball_launched = False

            # Process white detections for distance estimation
            for (wx, wy) in white_centroids:
                for (bc, bw, bh, bx, by) in black_info:
                    # Check proximity to use bounding box around this black cross
                    if abs(wx - bc[0]) < bw // 2 and abs(wy - bc[1]) < bh // 2:
                        bbox_x2 = bx + bw
                        bbox_y2 = by + bh
                        roi_disparity = disparity_map[by:bbox_y2, bx:bbox_x2].astype(np.float32)

                        if roi_disparity.size > 0:
                            mean_disparity = np.mean(roi_disparity) / 16.0
                            if mean_disparity > 0:
                                baseline_m = 0.075
                                focal_length_px = 870
                                distance_m = (focal_length_px * baseline_m) / mean_disparity

                                cv2.putText(frame, f'{distance_m:.2f}m', (wx + 10, wy),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
