import math

def analyze_gaze(detection_result, threshold):
    """
    Determines the gaze direction using ONLY head rotation.
    'threshold' is the value in degrees to trigger detection.
    Returns a tuple: (direction_key, full_display_string).
    """
    if not detection_result.facial_transformation_matrixes:
        return "N/A", "Gaze: N/A (Head not detected)"

    # Get the 4x4 transformation matrix
    matrix = detection_result.facial_transformation_matrixes[0]

    # --- EULER ANGLE EXTRACTION (Degrees) ---
    # Yaw: Left/Right rotation
    yaw = math.atan2(matrix[0, 2], matrix[0, 0])
    yaw_deg = math.degrees(yaw)

    # Pitch: Up/Down rotation
    pitch = math.atan2(-matrix[1, 2], math.sqrt(matrix[1, 0]**2 + matrix[1, 1]**2))
    pitch_deg = math.degrees(pitch)

    # Roll: Sideways tilt (head towards shoulder)
    roll = math.atan2(matrix[1, 0], matrix[0, 0])
    roll_deg = math.degrees(roll)

    # --- h_gaze DECISION LOGIC ---
    h_gaze = "Center"

    # Note: If the webcam is mirrored (default), a physical turn to the RIGHT 
    # usually produces a NEGATIVE Yaw value.
    if yaw_deg < -threshold:
        h_gaze = "Right"
    elif yaw_deg > threshold:
        h_gaze = "Left"

    # --- RETURN FORMATTED STRING ---
    # Create labels for debugging
    labels = (f"Yaw: {yaw_deg:+.1f}° | "
              f"Pitch: {pitch_deg:+.1f}° | "
              f"Roll: {roll_deg:+.1f}°")
    
    display_string = f"Gaze: {h_gaze}"
    
    return h_gaze, display_string