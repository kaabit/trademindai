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
