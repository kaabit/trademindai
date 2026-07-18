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
