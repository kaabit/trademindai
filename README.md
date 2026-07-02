# TradeMindAI Starter v4

TradeMindAI is a prototype AI-assisted customs document checker for importers, exporters, customs brokers, freight forwarders, and logistics teams.

## What is new in v4

- Fedora-friendly OCR detection was added. The app now looks for `/usr/bin/tesseract` automatically.
- OCR language fallback was improved: if only `eng` is installed, OCR still runs instead of failing on `eng+fra+ara`.
- Clear OCR status is shown in the sidebar.
- The camera is no longer opened by default.
- The user first chooses one input method:
  - Upload files
  - Take a picture
  - Paste text manually
- The camera appears only when **Take a picture** is selected.
- The UI uses the same global trade / AI background used in the product presentation.
- The UI language can be switched between English, French, and Arabic.
- Supported uploads: TXT, PDF, DOCX, PNG, JPG, JPEG, WEBP, TIFF.

## How to run

```bash
cd trademindai_starter_v4
pip install -r requirements.txt
streamlit run app.py
```

## Notes about image/photo analysis

The current prototype uses OCR for images and photos. It can work when Tesseract OCR is installed and the photo quality is clear.

For a production version, replace or enrich the OCR step with a vision-capable AI model so the tool can better understand scanned invoices, tables, stamps, signatures, and photos taken by phone.

## Compliance note

This tool is for decision support only. Final HS classification, customs declaration, duties, taxes, and compliance decisions must be validated by a qualified customs professional or customs authority.


## Fedora OCR setup

Your Fedora system may install only English OCR by default. For better French and Arabic image/photo analysis, run:

```bash
sudo dnf install tesseract tesseract-langpack-fra tesseract-langpack-ara
tesseract --list-langs
```

You should see `eng`, `fra`, and `ara`.

If Streamlit still cannot find Tesseract, run:

```bash
export TESSERACT_CMD=/usr/bin/tesseract
streamlit run app.py
```

## v5 updates
- Language switch now affects the main result sections, side options, tables, questions, and next steps.
- Amount extraction now shows only likely commercial monetary values with currency or total/amount labels. It no longer lists every number from OCR such as dates, invoice numbers, phone numbers, and quantities.
- HS extraction was tightened to avoid treating dates or invoice numbers as HS codes.
- Camera photo capture remains available. Video recording is not included in this prototype because the MVP analyzes customs documents from files, photos, or pasted text. Video can be added later with a custom Streamlit component if needed.


## v7 UI readability update

This version improves readability of dropdowns, input boxes, radio choices, file uploader, tables, and buttons on the dark presentation-style background.


## v9 UI update

- Changed the interface from the dark night background to a lighter day-world trade background.
- Improved the top header contrast so the white browser/Streamlit header does not hide the content.
- Updated form controls, upload area, radio choices, and buttons for better readability.

## v10 additions

- The app now shows the analysis model as `TradeMindAI Rules + HS/SH reference v10`.
- You can upload an HS/SH reference CSV from the sidebar.
- Expected CSV columns are: `code`, `description`, and optional `keywords`.
- A starter example is included in `reference_data/hs_sh_reference_sample.csv`.
- The app now detects object/product names declared in a manifest or document and compares them with the declared HS/SH code reference description.
- The match is a pre-check only. Final HS/SH classification must be validated by a qualified customs professional or customs broker.


## v11 manifest analysis improvements

This version improves cargo-manifest analysis. It now attempts to extract structured manifest line items and display:

- HS/SH code with the loaded reference meaning.
- Declared object/description from the manifest row.
- Declared commercial value linked to each cargo line.
- Manifest total declared value when detected.
- A clearer match check between the declared product description and the HS/SH reference description.

Example for the sample France to Tunisia manifest:

- 6109.10 -> T-shirts / cotton garments, declared value 12,700 EUR.
- 6203.42 -> Cotton trousers/pants, declared value 12,700 EUR.
- 8483.90 -> Mechanical spare parts, declared value 25,000 EUR.
- Total declared value -> 37,700 EUR.

The tool is still a pre-review assistant. Final HS classification and customs declaration must be validated by a qualified customs broker/customs professional.


## New in v15: HS/SH Classification Assistant

The app now includes a second feature page: **Determine HS code**.

Use the sidebar **Feature / Fonction / الوظيفة** selector to switch between:

- **Document review**: upload or paste customs documents and analyze fields, amounts, HS codes, and manifest descriptions.
- **Determine HS code**: describe the good, then move step by step from HS section to chapter, heading, and subheading. The user confirms a checklist and receives a proposed HS/SH code with a confidence score.

This is a prototype decision-support workflow. It does not replace final validation by a qualified customs professional or customs authority.
