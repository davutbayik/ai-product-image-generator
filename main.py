import io
import os
import logging
from openai import OpenAI
import gspread
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("process_logs.log", mode='a')
    ]
)

DRIVE_FOLDER_ID = "YOUR-DRIVE-FOLDER-ID-CONTAINS-PRODUCTS"
GOOGLE_SHEETS_ID = "YOUR-PRODUCT-GOOGLE-SHEETS-ID"

# Create output folder if not exists
os.makedirs("output", exist_ok=True)

# Define scopes for Google Drive/Sheets Integration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    # Get OpenAI API Key (store it in .env file)
    load_dotenv()

    # Initialize an OpenAI Client
    client = OpenAI()
    
    # Load credentials
    creds = Credentials.from_service_account_file("YOUR-GOOGLE-CLOUD-SERVICE-AUTH-JSON", scopes=SCOPES)

    # Authorize Google Sheets
    sheets_client = gspread.authorize(creds)
    drive_service = build("drive", "v3", credentials=creds)

    # === 1. Read Products ===
    sheet = sheets_client.open_by_key(GOOGLE_SHEETS_ID).worksheet("Products")
    products_data = sheet.get_all_records()

    logging.info("Successfully read product details!")

    for row in products_data:

        # Find the row and column indexes
        row_index = None
        for i, sub_row in enumerate(products_data, start=2):  # row 2 is the first data row
            if sub_row.get("ID") == row.get("ID"):
                row_index = i
                break
    
        if row.get("Description") != '' and row.get("ID") != '' and row.get("Status") == 'Pending':
            try:
                # === 2. Generate Image Prompt via OpenAI ===
                system_prompt = """
                    You are an AI assistant that specializes in generating image prompts for AI-based product mockup generation tools (e.g., DALL·E, Stable Diffusion).

                    You will receive structured product data. The field "Description" will always be present, but fields like "Category", "Color", "Material", and "Additional Notes" may or may not be included or may be empty.

                    Your task is to:
                        - Understand the product from the given information.
                        - Generate a single, visually rich, text-to-image prompt.
                        - The prompt should be suitable for generating a clean, realistic product mockup with no logos or text.
                        - If color or material is provided, include it.
                        - If the category or usage context is available (e.g., baby, home, office), include relevant background/staging elements.
                        - Be specific, descriptive, and concise (1–2 lines max).
                        - Output only the single string prompt.

                    **INPUT FORMAT (JSON):**
                        {
                            "Description": "Silicone baby feeding set with bowl, plate, and spoon.",
                            "Category": "Baby Products",
                            "Color": "Pastel Blue",
                            "Material": "Food-grade silicone",
                            "Additional Notes": "For toddler self-feeding, suction base"
                        }

                    **OUTPUT FORMAT:**
                        "A pastel blue silicone baby feeding set (bowl, plate, spoon) on a wooden high chair tray in a soft-lit kitchen, toddler setting, clean background"
                """

                product_input = {
                    "Description": row.get("Description", ""),
                    "Category": row.get("Category"),
                    "Color": row.get("Color"),
                    "Material": row.get("Material"),
                    "Additional Notes": row.get("Additional Notes")
                }

                user_prompt = f"Generate a product mockup image prompt from:\n{product_input}"

                response = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[{"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}]
                    )

                image_prompt = response.choices[0].message.content.strip()

                logging.info("Successfully created text-to-image prompt!")
                logging.info(f"Text-to-Image Prompt: {image_prompt}")
                
                # === 3. Generate Image from Prompt ===
                image_response = client.images.generate(
                    model="gpt-image-1",  # or "dall-e-3"
                    prompt=image_prompt,
                    size="1024x1024",
                    n=1
                )

                base64_image = image_response.data[0].b64_json

                # Decode and write the image
                image_data = base64.b64decode(base64_image)

                with open(f"output/mockup_id_{row.get('ID')}.png", "wb") as f:
                    f.write(image_data)

                logging.info("Successfully generated mockup image!")
                
                # === 4. Upload to Google Drive ===
                file_metadata = {
                    'name': f'generated_id_{row.get("ID")}.png',
                    'parents': [DRIVE_FOLDER_ID] if DRIVE_FOLDER_ID else []
                }

                media = MediaIoBaseUpload(io.BytesIO(image_data), mimetype='image/png')
                uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields='id,webContentLink').execute()

                logging.info(f"Image uploaded to Google Drive Folder: {uploaded['webContentLink']}")
                
                # === 5. Update Google Sheet ===
                sheet.update_cell(row_index, list(row.keys()).index("Status") + 1, "Completed")
                logging.info(f"Status of the product changed to 'Completed' in Google Sheets!")
                
            except Exception as e:
                logging.error(f"Encountered an error during image generation for product ID - {row.get("ID")}:\n{e}")
                sheet.update_cell(row_index, list(row.keys()).index("Status") + 1, "Error")
                
                logging.info(f"Status of the product changed to 'Error' in Google Sheets!")
        
        else:
            logging.error("Product details missing or product status is not 'Pending'. Process terminated!")
            sheet.update_cell(row_index, list(row.keys()).index("Status") + 1, "Error")
                
            logging.info(f"Status of the product changed to 'Error' in Google Sheets!")
        
except Exception as e:
    logging.error(f"Encountered an error: {e}")