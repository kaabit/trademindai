# Streamlit Cloud deployment notes

For image/photo OCR, the app needs both Python packages and the Tesseract system package.

## Required files

`requirements.txt` installs Python dependencies:
- streamlit
- pandas
- pypdf
- python-docx
- pillow
- pytesseract

`packages.txt` installs Linux system dependencies on Streamlit Cloud:
- tesseract-ocr
- tesseract-ocr-eng
- tesseract-ocr-fra
- tesseract-ocr-ara

After adding or changing `packages.txt`, redeploy or reboot the app in Streamlit Cloud.

## Important limitation

OCR reads text inside documents or photos. It does not visually recognize objects from a pure product photo. For true object identification from images, connect a vision-capable AI model in a later production version.


## AI vision setup for product-photo identification

OCR can only read text from images. To identify the object in a pure product photo, add this secret in Streamlit Cloud:

```toml
OPENAI_API_KEY = "your_api_key_here"
OPENAI_VISION_MODEL = "gpt-4o-mini"
```

Then redeploy/reboot the app. Without this key, the app will still work for typed descriptions and OCR-readable documents, but it cannot visually identify products from photos.


## Google Cloud Vision setup for product-photo identification

OCR only reads visible text. Google Cloud Vision can identify product labels from a pure product photo.

1. Create or select a Google Cloud project.
2. Enable the Cloud Vision API.
3. Create a service account with permission to use Cloud Vision.
4. Create a JSON key for that service account.
5. In Streamlit Cloud, open App settings > Secrets and paste the JSON as:

```toml
GOOGLE_APPLICATION_CREDENTIALS_JSON = """
{ ... full service account JSON ... }
"""
```

Then redeploy/reboot the app.

The app uses Google Cloud Vision label/object detection first. If no Google credentials are configured, it can still use OpenAI vision fallback when `OPENAI_API_KEY` is configured.


## Alternative when service account key creation is disabled

If Google Cloud blocks service account JSON key creation with `iam.disableServiceAccountKeyCreation`, use an API key instead:

1. Open Google Cloud Console > APIs & Services > Credentials.
2. Click Create credentials > API key.
3. Restrict the key to the Cloud Vision API.
4. In Streamlit Cloud > App settings > Secrets, add:

```toml
GOOGLE_VISION_API_KEY = "your-api-key"
```

Then redeploy/reboot the app.
