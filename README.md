# python-gui-drop-analysis

The Video Analysis Tool is a graphical user interface (GUI) application built using Python and Tkinter for video analysis. It allows users to select, crop, and rotate video frames, set baselines, and queue videos for analysis.

## Features

- **Video Selection**: Browse and select video files for analysis.
- **Target Path Selection**: Choose a directory to save the analysis results.
- **Image Cropping**: Select and crop images from the video frames.
- **Image Rotation**: Rotate images by a specified degree.
- **Baseline Selection**: Set a baseline for the cropped image.
- **Queue Videos**: Add videos to a queue for batch processing.
- **Start Analysis**: Analyze queued videos with the specified parameters.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/video-analysis-tool.git
    cd video-analysis-tool
    ```

2. **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install the required packages**:
    ```bash
    pip install tkinter
    pip install cv2
    ```

## Usage

1. **Run the application**:
    ```bash
    python main.py
    ```

2. **Follow the steps below to use the tool**:
    - **Select Video**: Click on "Browse" next to "Select Video" to choose a video file.
    - **Select Target Path**: Click on "Browse" next to "Select Target Path" to choose a directory for saving results.
    - **Crop Image**: Click on "Select Image from Video" to open a video frame selection window. Choose a frame, then crop the image as needed.
    - **Rotate Image**: Enter the desired rotation angle in the "Rotate Image (degrees)" field and press Enter.
    - **Select Baseline**: Use the slider to set a baseline for the cropped image.
    - **Add to Queue**: Click "Add to Queue" to queue the video for analysis. The parameters will reset after adding to the queue.
    - **Start Analysis**: Click "Start Analysis" to analyze the queued videos.