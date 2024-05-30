from google.cloud import translate_v2 as translate
from google.cloud import vision
import os
from PIL import Image, ImageDraw, ImageFont
import html

def upload_and_translate(input_dir, output_dir, target_language, merge_threshold=10):
    # Ensure input and output directories exist
    if not os.path.exists(input_dir):
        raise ValueError(f"Input directory {input_dir} does not exist.")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize Google Translate client
    translate_client = translate.Client()

    # Initialize Google Vision client
    vision_client = vision.ImageAnnotatorClient()

    # Get a list of all the files in the input directory
    files = os.listdir(input_dir)

    # Filter images: only take JPEG and PNG files
    image_files = [file for file in files if file.lower().endswith(('jpg', 'jpeg', 'png'))]

    def get_font(font_size):
        """Try multiple font paths to find one that works."""
        font_paths = [
            "./Montserrat-Bold.ttf",  # 
        ]
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, font_size)
            except IOError:
                continue
        return ImageFont.load_default()

    # Iterate over the files and process them
    for file in image_files:
        file_name, file_extension = os.path.splitext(file)
        input_path = os.path.join(input_dir, file)
        output_path = os.path.join(output_dir, file_name + "_translated" + file_extension)

        with open(input_path, "rb") as image_file:
            content = image_file.read()
            image = vision.Image(content=content)
            
            # Perform text detection on the image file
            response = vision_client.text_detection(image=image)
            annotations = response.text_annotations

            if annotations:
                # Open the image using PIL without alpha channel support
                with Image.open(input_path).convert('RGB') as img:
                    image_width, image_height = img.size
                    
                    # Get a drawing context
                    draw = ImageDraw.Draw(img)

                    # Prepare text merging
                    merged_phrases = []
                    current_box = None
                    current_text = ""
                    
                    for annotation in annotations[1:]:  # Skip the entire detected text
                        # Get the bounding box vertices and prepare box dimensions
                        vertices = annotation.bounding_poly.vertices
                        left = vertices[0].x
                        top = vertices[0].y
                        right = vertices[2].x
                        bottom = vertices[2].y

                        if current_box:
                            # Check horizontal and vertical proximity
                            if left - current_box[2] <= merge_threshold and abs(current_box[1] - top) <= merge_threshold:
                                # Merge current text and adjust bounding box
                                current_text += " " + annotation.description
                                current_box = (min(current_box[0], left), min(current_box[1], top), max(current_box[2], right), max(current_box[3], bottom))
                            else:
                                # Append the current box and reset for new phrase
                                merged_phrases.append((current_box, current_text))
                                current_text = annotation.description
                                current_box = (left, top, right, bottom)
                        else:
                            current_text = annotation.description
                            current_box = (left, top, right, bottom)
                    
                    # Append the last box
                    if current_box:
                        merged_phrases.append((current_box, current_text))

                    for box, text in merged_phrases:
                        box_left, box_top, box_right, box_bottom = map(int, [min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3])])
                        box_width = box_right - box_left
                        box_height = box_bottom - box_top

                        # Adjust font size relative to the bounding box height
                        font_size = int(box_height * 0.6)  # Adjust the multiplier as needed
                        font = get_font(font_size)

                        # Translate text
                        translation = translate_client.translate(text, target_language=target_language)
                        translated_text = translation['translatedText']

                        # Handle special characters (HTML entities)
                        translated_text = html.unescape(translated_text)

                        # Calculate text size to center text
                        text_bbox = font.getbbox(translated_text)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]

                        # Padding values
                        padding_left = 2

                        # Calculate text position to be centered with padding
                        text_x = box_left + (box_width - text_width) / 2 + padding_left
                        text_y = box_top + (box_height - text_height) / 2 + 0

                        # Draw rounded rectangle with gray background (no transparency)
                        draw.rounded_rectangle((box_left, box_top, box_right, box_bottom), radius=10, fill=(169, 169, 169))  # Solid gray

                        # Draw the centered text
                        draw.text((text_x, text_y), translated_text, fill="black", font=font)

                    # Save the modified image to the output directory
                    img.save(output_path)

# Example usage:
if __name__ == "__main__":
    input_dir = "./input"
    output_dir = "./output"
    target_language = "en"
    upload_and_translate(input_dir, output_dir, target_language)