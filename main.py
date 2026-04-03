import cv2
import mediapipe as mp
import time
import sys
import os
import tkinter as tk
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gaze_analyzer import analyze_gaze
from ui_controller import UIController

def resource_path(relative_path):
    """ Gets the absolute path to a resource, works for dev and for PyInstaller. """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    """
    Main function that captures video from the webcam, analyzes gaze,
    and updates the UI in real-time.
    """

    ui = UIController()
    detector = None
    cap = cv2.VideoCapture(0)

    try:
        # --- 1. MEDIAPIPE INITIALIZATION ---
        model_path = resource_path('face_landmarker.task')
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            output_facial_transformation_matrixes=True,
            num_faces=1)
        detector = vision.FaceLandmarker.create_from_options(options)

        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        # --- 2. MAIN LOOP ---
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("End of video stream or read error.")
                break

            # Flip the image horizontally for a selfie-view display and convert to RGB
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(time.time() * 1000)

            # Before accessing UI elements, check if the window still exists.
            # This prevents a TclError if the user closes the window.
            try:
                if not ui.root.winfo_exists():
                    break
            except tk.TclError:
                # This will be raised if the window is destroyed completely.
                break

            # --- 3. DETECTION, ANALYSIS, AND UI UPDATE ---
            display_text = "Analysis paused. Press Start." # Default text

            # Only run analysis if started from the UI
            if ui.is_analysis_running():
                # Get the current threshold from the UI
                current_threshold = ui.get_threshold()

                detection_result = detector.detect_for_video(mp_image, timestamp_ms)
                direction, display_text = analyze_gaze(detection_result, current_threshold)
                ui.update_highlight(direction)

            # Always update the UI window. If it's closed, break the loop.
            try:
                ui.root.update()
            except tk.TclError:
                break

            # --- 4. DISPLAY (DEBUG) ---
            # Add text to the frame regardless of whether it's shown
            cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Show or hide the webcam feed based on the UI toggle
            if ui.is_webcam_visible():
                cv2.imshow('Webcam Feed', frame)
                # If the user closes the window with the 'X' button, update the UI state
                try:
                    if cv2.getWindowProperty('Webcam Feed', cv2.WND_PROP_VISIBLE) < 1:
                        ui.toggle_webcam_visibility()
                except cv2.error:
                    pass # Window was likely already destroyed, which is fine
            else:
                # If the window is not supposed to be visible, try to close it.
                # This handles the case where the user clicks "Hide Webcam".
                try:
                    cv2.destroyWindow('Webcam Feed')
                except cv2.error:
                    # This error occurs if the window doesn't exist, which is fine.
                    pass

            key = cv2.waitKey(5) & 0xFF
            if key == 27 and ui.is_webcam_visible(): # If ESC is pressed while webcam is visible
                ui.toggle_webcam_visibility() # Just hide the webcam
    finally:
        if detector:
            detector.close()
        if cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        try:
            ui.root.destroy()
        except tk.TclError:
            # This can happen if the window is already destroyed, which is fine.
            pass

if __name__ == "__main__":
    main()
