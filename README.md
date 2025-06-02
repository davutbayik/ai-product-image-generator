# 🛍️ AI-Powered Product Mockup Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.0-green)

Automatically generate commercial-quality product mockup images using OpenAI and Google Workspace integrations (Sheets + Drive).

---

## ✨ Features

* 🔎 Reads product data from a Google Sheet
* 🧠 Uses GPT-4 to generate visual mockup prompts
* 🎨 Generates product images using OpenAI image API
* 💾 Saves generated mockups to a local folder
* ☁️ Uploads images to a specific Google Drive folder
* ✅ Updates the status of each processed product in the original Google Sheet
* 📜 Logs all processing steps and errors

---

## 📁 Folder Structure

```
project/
├── output/                      # Saved mockup images
├── .env                         # Environment file with OpenAI API key
├── YOUR-GOOGLE-CLOUD-SERVICE-AUTH-JSON
├── process_logs.log             # Log file
├── main.py                      # Main script (provided above)
```

---

## 🎥 Example Demo


https://github.com/user-attachments/assets/54a42888-9920-4340-a46d-ebe20cf9f960


---

## 🛠️ Installation

1. Clone the repository:
   
   ```bash
   git clone https://github.com/davutbayik/ai-product-image-generator.git
   cd ai-product-image-generator

2. Create and activate a virtual environment (Optional-Recommended):
   
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. Install the required packages:
   
   ```bash
   pip install -r requirements.txt

4. Set Up `.env`:
   
   Create a `.env` file with your OpenAI API key:
   
   ```ini
   OPENAI_API_KEY=sk-xxxxxxx
   ```

5. Set Up Google Cloud Credentials:
     
     * Go to [Google Cloud Console](https://console.cloud.google.com/)
     * Enable **Google Sheets API** and **Google Drive API**
     * Create a service account and download the JSON key
     * Share your **Google Sheet** and **Google Drive Folder** with the service account email

6. Add Folder and Sheet IDs:
 
     Update this part in your code:
     
     ```python
     DRIVE_FOLDER_ID = "your-google-drive-folder-id"
     GOOGLE_SHEETS_ID = "your-google-sheets-id"
     ```

7. Run the Script:

     ```bash
     python main.py
     ```

---

## 🧪 Example Sheet Structure

| ID   | Description                                | Category      | Color       | Material            | Additional Notes           | Status  |
| ---- | ------------------------------------------ | ------------- | ----------- | ------------------- | -------------------------- | ------- |
| 1001 | Silicone baby feeding set with bowl, spoon | Baby Products | Pastel Blue | Food-grade silicone | Suction base, toddler safe | Pending |

> The script will only process rows with `Status = Pending`

---

## 🛠️ Prompt Logic (GPT System Prompt)

* Understands fields like `Description`, `Category`, `Color`, `Material`, and `Additional Notes`
* Generates clean, realistic mockup prompts for DALL·E / OpenAI Image API or other image generation APIs

---

## 🔐 Security

* Do not upload your `.env` or service account JSON to any public repository

---

## 💡 Future Improvements

* Add UI with Streamlit for manual input or preview
* Enable batch download of all generated images
* Add error reporting via email or Slack

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).  
You are free to use, modify, and distribute this software as long as you include the original license.

## 📬 Contact

Made with ❤️ by [Davut Bayık](https://github.com/davutbayik) — feel free to reach out via GitHub for questions, feedback, or collaboration ideas.

---

⭐ If you found this project helpful, consider giving it a star!
