import pytesseract

print(pytesseract)

pytesseract.pytesseract.tesseract_cmd = r"C:/Users/ydefontaine/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"

image_path = "OCR/test/24. Fiche CARD-i Saint-Clar-de-Rivière.pdf_page_6.png"

text = pytesseract.image_to_string(image_path)

print(text)

# import asyncio
# import io
# import re

# import fitz
# import pytesseract
# from PIL import Image

# Image.MAX_IMAGE_PIXELS = None


# async def pix_to_image(pix: fitz.Pixmap) -> Image.Image:
#     """
#     Convert a fitz.Pixmap object to a PIL.Image object.

#     Args:
#         pix (fitz.Pixmap): The Pixmap object to be converted.

#     Returns:
#         PIL.Image: The converted Image object.
#     """
#     # Get the raw pixel data
#     pixel_data = pix.samples

#     # Determine the mode and size
#     if pix.n == 4:  # RGBA
#         mode = "RGBA"
#     elif pix.n == 3:  # RGB
#         mode = "RGB"
#     else:
#         raise ValueError("Unsupported number of components: {}".format(pix.n))

#     size = (pix.width, pix.height)

#     # Create the PIL.Image object
#     image = Image.frombytes(mode, size, pixel_data)

#     return image


# async def process_page(pdf_path: str) -> list[str]:
#     """
#     Converts each page of a PDF into an image.

#     Args:
#         pdf_path (str): The file path to the PDF document.

#     Returns:
#         list[str]: A list of the processed images.
#     """
#     # print(f"start pdf_to_image_files: {pdf_path}")
#     image_paths = []
#     object_images = []
#     with fitz.open(pdf_path) as doc:
#         for page_num in range(doc.page_count):
#             page = doc.load_page(page_num)
#             pix = page.get_pixmap(
#                 matrix=fitz.Matrix(300 / 72, 300 / 72)
#             )  # Set image resolution
#             image_path = f"{pdf_path}_page_{page_num}.png"
#             image_paths.append(image_path)
#             image = await pix_to_image(pix)
#             object_images.append(image)
#     precessed_pages = await process_images_in_parallel_pil(image_paths, object_images)
#     # print(f"end pdf_to_image_files: {pdf_path}")
#     return precessed_pages


# async def pdf_to_image_files(pdf_paths: list[str]) -> list[str]:
#     """
#     Converts a list of PDF file paths to a list of image file paths.
#     Args:
#         pdf_paths (list[str]): A list of PDF files paths to be processed.
#     Returns:
#         list[str]: A list of the generated image file paths.
#     """
#     processed_images = []

#     tasks = [process_page(pdf_path) for pdf_path in pdf_paths]
#     results = await asyncio.gather(*tasks)
#     for result in results:
#         processed_images.extend(result)

#     # with ThreadPoolExecutor() as executor:
#     #     futures = {
#     #         executor.submit(process_page, pdf_path): pdf_path for pdf_path in pdf_paths
#     #     }
#     #     for future in as_completed(futures):
#     #         processed_images.extend(future.result())

#     return processed_images


# async def process_single_image_path(image_path: str) -> str:
#     """
#     Processes a single image located at the given path by resizing and rotating it if necessary.
#     Args:
#         image_path (str): The file path to the image to be processed.
#     Returns:
#         str: The file path to the processed image.
#     """
#     with Image.open(image_path) as img:
#         width, height = img.width, img.height
#         max_length = max(width, height)
#         if max_length > 4000:
#             ratio = float(4000 / max_length)
#             new_dimensions = (int(img.width * ratio), int(img.height * ratio))
#             img = img.resize(new_dimensions, Image.Resampling.LANCZOS)

#         image_size = await get_image_size_in_mb(img)
#         if image_size > 3.5:
#             width, height = img.width, img.height
#             ratio = float(3.5 / image_size)
#             new_dimensions = (int(img.width * ratio), int(img.height * ratio))
#             # Resize the image
#             resized_img = img.resize(new_dimensions, Image.Resampling.LANCZOS)
#             rotated_image = await rotate_image(resized_img)
#             rotated_image.save(image_path)
#         else:
#             rotated_image = await rotate_image(img)
#             rotated_image.save(image_path)

#         return image_path


# async def process_single_image_pil(image_path: str, image: Image.Image) -> str:
#     """
#     This function resizes the image if its dimensions exceed 4000 pixels in either width or height,
#     maintaining the aspect ratio. It also ensures that the image size does not exceed 3.5 MB by
#     resizing it accordingly.
#     Args:
#         image_path (str): The file path where the processed image will be saved.
#         image (Image.Image): The PIL Image object to be processed.
#     Returns:
#         str: The file path where the processed image is saved.
#     """
#     width, height = image.width, image.height
#     max_length = max(width, height)
#     if max_length > 4000:
#         ratio = float(4000 / max_length)
#         new_dimensions = (int(image.width * ratio), int(image.height * ratio))
#         image = image.resize(new_dimensions, Image.Resampling.LANCZOS)

#     image_size = await get_image_size_in_mb(image)
#     if image_size > 3.5:
#         width, height = image.width, image.height
#         ratio = float(3.5 / image_size)
#         new_dimensions = (int(image.width * ratio), int(image.height * ratio))
#         # Resize the image
#         resized_img = image.resize(new_dimensions, Image.Resampling.LANCZOS)
#         rotated_image = await rotate_image(resized_img)
#         rotated_image.save(image_path)
#     else:
#         rotated_image = await rotate_image(image)
#         rotated_image.save(image_path)

#     return image_path


# async def process_images_in_parallel_path(image_paths: list[str]) -> list[str]:
#     """
#     Process multiple images in parallel.

#     Args:
#         image_paths (list[str]): A list of file paths to the images.

#     Returns:
#         list[str]: A list of the processed images.
#     """

#     processed_images = [
#         process_single_image_path(image_path) for image_path in image_paths
#     ]
#     return await asyncio.gather(*processed_images)

#     # processed_images = []
#     # with ThreadPoolExecutor() as executor:
#     #     futures = {
#     #         executor.submit(process_single_image, image_path): image_path
#     #         for image_path in image_paths
#     #     }
#     #     for future in as_completed(futures):
#     #         processed_images.append(future.result())

#     # return processed_images


# async def process_images_in_parallel_pil(
#     image_paths: list[str], images_object: list[Image.Image]
# ) -> list[str]:
#     """
#     Processes a list of images in parallel using PIL (Python Imaging Library).
#     Args:
#         image_paths (list[str]): A list of file paths to the images to be processed.
#         images_object (list[Image.Image]): A list of PIL Image objects corresponding to the image paths.
#     Returns:
#         list[str]: A list of results from processing each image.
#     """

#     processed_images = [
#         process_single_image_pil(image_path, image_object)
#         for image_path, image_object in zip(image_paths, images_object)
#     ]
#     return await asyncio.gather(*processed_images)


# async def detect_orientation(image: Image.Image) -> int:
#     """
#     Detect the orientation of the given image and return the angle needed to correct it.

#     This function uses Tesseract's OSD (Orientation and Script Detection) to determine the rotation angle
#     of the image. The angle is then corrected to ensure the image is properly oriented.

#     Args:
#         image (Image.Image): The image to be analyzed.

#     Returns:
#         int: The angle (in degrees) needed to rotate the image to the correct orientation.
#     """
#     try:
#         # Resize the image to speed up processing
#         resized_image = image.resize(
#             (image.width // 2, image.height // 2), Image.Resampling.LANCZOS
#         )

#         osd = pytesseract.image_to_osd(resized_image)
#         match = re.search(r"Rotate: (\d+)", osd)
#         if match:
#             angle = await correct_rotation_angle(int(match.group(1)))
#             return angle
#         else:
#             print("No rotation angle found in OSD output.")
#     except pytesseract.TesseractError as e:
#         print(f"Tesseract error detecting orientation: {e}")
#     except Exception as e:
#         print(f"Unexpected error detecting orientation: {e}")
#     return 0


# async def correct_rotation_angle(angle: int) -> int:
#     """
#     Correct the rotation angle to the nearest major rotation (0, 90, 180, 270 degrees).

#     This function takes an angle and determines the closest major rotation angle.

#     Args:
#         angle (int): The angle to be corrected.

#     Returns:
#         int: The corrected angle.
#     """
#     if angle <= 45 or angle > 315:
#         return 0
#     if 45 < angle <= 135:
#         return 90
#     if 135 < angle <= 225:
#         return 180
#     if 225 < angle <= 315:
#         return 270
#     return 0


# async def get_image_size_in_mb(image: Image.Image) -> float:
#     """
#     Get the size of a PIL.Image object in megabytes.

#     Args:
#         image (PIL.Image.Image): The image object.

#     Returns:
#         float: The size of the image in megabytes.
#     """
#     # Create an in-memory buffer
#     buffer = io.BytesIO()

#     # Save the image to the buffer
#     image.save(buffer, format="PNG")  # You can change the format if needed

#     # Get the size of the buffer in bytes
#     size_in_bytes = buffer.getbuffer().nbytes

#     # Convert the size to megabytes
#     size_in_mb = size_in_bytes / (1024 * 1024)

#     return size_in_mb


# async def rotate_image(img: Image.Image) -> Image.Image:
#     """
#     Asynchronously rotates an image based on its detected orientation.
#     Args:
#         img (Image.Image): The image to be rotated.
#     Returns:
#         Image.Image: The rotated image.
#     """
#     angle = await detect_orientation(img)
#     # Rotate the image based on the detected angle
#     if angle == 90:
#         rotated_image = img.rotate(-90, expand=True)
#     elif angle == 180:
#         rotated_image = img.rotate(-180, expand=True)
#     elif angle == 270:
#         rotated_image = img.rotate(-270, expand=True)
#     else:
#         rotated_image = img

#     return rotated_image


# async def main():
#     pdf_paths = ["OCR/test/24. Fiche CARD-i Saint-Clar-de-Rivière.pdf"]
#     image_paths = await pdf_to_image_files(pdf_paths)
#     print(f"Processed images: {image_paths}")

# if __name__ == "__main__":
#     main()
