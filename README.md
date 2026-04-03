# Tellme

This project uses a webcam and Google's MediaPipe library to track a person's head direction in real-time.
It is a simple, rapidly developed ("vibe-coded") project created with a clear purpose: to help individuals with communication difficulties express themselves. Users can communicate in an accessible way simply by moving their head to select custom-loaded images.

# Features

Head Rotation Detection: Tracks right, left, and center head movements using MediaPipe.

Custom Image Loading: Upload your own symbolic images to build a personalized communication interface.

User-Friendly GUI: A simple graphical interface allows you to easily start or pause the analysis and adjust the tracking sensitivity.

Live Feedback: Displays the webcam feed with an on-screen indicator of the current head direction.

# Prerequisites

* Python 3.8 or higher
* A webcam
* Required Python libraries (listed in the requirements.txt file)
* [download](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task) the model
