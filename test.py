# Get list of image files in the Train_data folder
import os
import glob

# print(os.getcwd())
# print(os.path.exists("Train_data/"))
# print(os.listdir("Train_data/"))

from ultralytics import YOLO

# Load a pre-trained YOLOv10n model
model = YOLO("yolov10n.pt")

# Define the path to the Train_data folder
train_data_folder = "Train_data/"

# Get a list of all image files in the folder
image_files = glob.glob(os.path.join(train_data_folder, "*.jpg"))

# Perform object detection on an image
results = model(image_files[1])

# Show result
results[0].show()


# Loop through the image files
# for image_file, i in enumerate(image_files):
#     print(f"Processing image: {image_file}")

#     # Perform object detection on an image
#     results = model(image_file)

#     # Save the results to a file
#     results[0].save("image_file" + str(i) + ".jpg")
