import sys
try:
    from pyk4a import PyK4A, Config
    import imageio
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure pyk4a and imageio are installed: pip3 install pyk4a imageio")
    sys.exit(1)

print("Initializing Azure Kinect DK...")

try:
    # Initialize the camera
    k4a = PyK4A(Config())
    k4a.start()
    print("Camera started successfully!")

    # Capture a single frame
    print("Capturing frame...")
    capture = k4a.get_capture()

    if capture.color is not None:
        imageio.imwrite("color_image.jpg", capture.color)
        print("Color image saved as color_image.jpg")
        print(f"Image shape: {capture.color.shape}")
    else:
        print("Failed to capture color image.")

    if capture.depth is not None:
        imageio.imwrite("depth_image.png", capture.depth)
        print("Depth image saved as depth_image.png")
        print(f"Depth image shape: {capture.depth.shape}")
    else:
        print("Failed to capture depth image.")

    k4a.stop()
    print("Test completed successfully!")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure your Azure Kinect DK is properly connected.")
    sys.exit(1)
