import io
import os
import re
import shutil
from datetime import datetime, UTC
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
import json

st.set_page_config(page_title="TradeMindAI", page_icon="🌍", layout="wide")

# -----------------------------
# Visual theme: uses the same background concept as the presentation
# -----------------------------
def apply_trademind_theme():
    import base64
    from pathlib import Path
    # Daylight version of the world-trade background for clearer reading.
    bg_path = Path(__file__).parent / "assets" / "background_day.png"
    if not bg_path.exists():
        bg_path = Path(__file__).parent / "assets" / "background.png"
    if bg_path.exists():
        encoded = base64.b64encode(bg_path.read_bytes()).decode()
        st.markdown(f"""
        <style>
        /* Remove the unclear white Streamlit top header and use a clean daylight theme. */
        [data-testid="stHeader"] {{
            background: rgba(232, 244, 255, 0.92) !important;
            border-bottom: 1px solid rgba(15, 54, 92, 0.14) !important;
        }}
        [data-testid="stToolbar"], [data-testid="stDecoration"] {{
            color: #0B2545 !important;
        }}
        .stApp {{
            background-image: linear-gradient(rgba(242, 248, 255, 0.62), rgba(231, 242, 255, 0.72)), url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #0B2545 !important;
        }}
        section.main > div {{
            padding-top: 2rem !important;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(245, 249, 255, 0.98), rgba(222, 237, 252, 0.98)) !important;
            border-right: 1px solid rgba(15, 54, 92, 0.18) !important;
        }}
        [data-testid="stSidebar"] * {{
            color: #0B2545 !important;
        }}
        h1, h2, h3, .stMarkdown, .stText, label, p {{
            color: #0B2545 !important;
        }}
        div[data-testid="stMarkdownContainer"] {{
            color: #0B2545 !important;
        }}
        /* Strong, clear inputs and dropdowns */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        textarea,
        input {{
            background-color: rgba(255, 255, 255, 0.98) !important;
            color: #061A33 !important;
            border: 1.5px solid rgba(8, 82, 148, 0.55) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(6, 26, 51, 0.08) !important;
        }}
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div,
        div[data-baseweb="input"] input,
        textarea,
        textarea::placeholder,
        input::placeholder {{
            color: #061A33 !important;
            opacity: 1 !important;
        }}
        /* Dropdown menu options */
        ul[role="listbox"],
        div[role="listbox"] {{
            background-color: #FFFFFF !important;
            color: #061A33 !important;
            border: 1px solid rgba(8, 82, 148, 0.35) !important;
        }}
        li[role="option"],
        div[role="option"],
        div[role="option"] * {{
            color: #061A33 !important;
            background-color: #FFFFFF !important;
        }}
        li[role="option"]:hover,
        div[role="option"]:hover,
        div[role="option"][aria-selected="true"] {{
            background-color: #DCEEFF !important;
            color: #061A33 !important;
        }}
        /* Clear radio choices */
        div[role="radiogroup"] {{
            gap: 12px;
        }}
        div[role="radiogroup"] label {{
            background: rgba(255, 255, 255, 0.92) !important;
            border: 1.5px solid rgba(8, 82, 148, 0.45) !important;
            border-radius: 12px !important;
            padding: 9px 13px !important;
            margin-right: 8px !important;
            box-shadow: 0 2px 8px rgba(6, 26, 51, 0.10) !important;
        }}
        div[role="radiogroup"] label p {{
            color: #0B2545 !important;
            font-weight: 800 !important;
        }}
        /* File uploader visibility */
        section[data-testid="stFileUploader"] {{
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 12px !important;
            border: 1.5px solid rgba(8, 82, 148, 0.42) !important;
            padding: 10px !important;
            box-shadow: 0 2px 10px rgba(6, 26, 51, 0.10) !important;
        }}
        section[data-testid="stFileUploader"] * {{
            color: #061A33 !important;
        }}
        button[kind="secondary"], button[kind="primary"], .stButton > button {{
            font-weight: 800 !important;
            border-radius: 10px !important;
        }}
        .stButton > button {{
            background-color: #0B65B1 !important;
            color: #FFFFFF !important;
            border: 1px solid #0B65B1 !important;
            box-shadow: 0 2px 8px rgba(6, 26, 51, 0.18) !important;
        }}
        /* Tables and JSON outputs should be readable */
        [data-testid="stDataFrame"] *,
        pre, code {{
            color: #061A33 !important;
        }}
        .trade-card {{
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(8, 82, 148, 0.20);
            border-radius: 18px;
            padding: 18px;
            backdrop-filter: blur(8px);
            margin-bottom: 14px;
            box-shadow: 0 8px 28px rgba(6, 26, 51, 0.10);
        }}
        .trade-title {{
            font-size: 48px;
            font-weight: 900;
            color: #0B2545;
            margin-bottom: 0;
            text-shadow: 0 1px 0 rgba(255,255,255,0.75);
        }}
        .trade-subtitle {{
            font-size: 20px;
            color: #123B63 !important;
            max-width: 980px;
            font-weight: 600;
        }}
        .trade-notice {{
            background: rgba(226, 241, 255, 0.95) !important;
            color: #0B2545 !important;
            border: 1px solid rgba(8, 82, 148, 0.22) !important;
        }}
        </style>
        """, unsafe_allow_html=True)

apply_trademind_theme()

# -----------------------------
# Optional document extraction
# -----------------------------
def safe_import(module_name: str):
    try:
        return __import__(module_name)
    except Exception:
        return None


def get_tesseract_cmd():
    """Find the local Tesseract executable.

    Fedora normally installs it at /usr/bin/tesseract. Some Streamlit
    environments do not inherit the shell PATH, so we check common paths too.
    """
    import os
    import shutil

    env_cmd = os.environ.get("TESSERACT_CMD")
    if env_cmd and os.path.exists(env_cmd):
        return env_cmd

    found = shutil.which("tesseract")
    if found:
        return found

    for candidate in [
        "/usr/bin/tesseract",
        "/app/.apt/usr/bin/tesseract",
        "/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/opt/homebrew/bin/tesseract",
        "/usr/local/opt/tesseract/bin/tesseract",
        r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
    ]:
        if os.path.exists(candidate):
            return candidate

    return ""


def get_available_ocr_languages(pytesseract_module) -> List[str]:
    try:
        langs = pytesseract_module.get_languages(config="")
        return sorted(langs)
    except Exception:
        return []


def choose_ocr_language(pytesseract_module) -> Tuple[str, str]:
    """Use available language packs. Prefer English+French+Arabic, fallback safely.

    This avoids failing when only 'eng' is installed, which is the default on many Fedora systems.
    """
    available = get_available_ocr_languages(pytesseract_module)
    preferred = [lang for lang in ["eng", "fra", "ara"] if lang in available]
    if preferred:
        missing = [lang for lang in ["fra", "ara"] if lang not in available]
        note = ""
        if missing:
            note = (
                "OCR ran with available language pack(s): "
                + ", ".join(preferred)
                + ". For better French/Arabic OCR on Fedora, install: "
                + "sudo dnf install tesseract-langpack-fra tesseract-langpack-ara"
            )
        return "+".join(preferred), note
    # Last-resort: let Tesseract use its default language if list detection failed.
    return "eng", "Could not list OCR languages; falling back to English OCR."


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, str]:
    pypdf = safe_import("pypdf")
    if pypdf is None:
        return "", "PDF text extraction needs: pip install pypdf"
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text, ""
    except Exception as exc:
        return "", f"Could not extract PDF text: {exc}"


def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, str]:
    docx = safe_import("docx")
    if docx is None:
        return "", "Word text extraction needs: pip install python-docx"
    try:
        document = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join(p.text for p in document.paragraphs)
        return text, ""
    except Exception as exc:
        return "", f"Could not extract Word text: {exc}"


def extract_text_from_image(file_bytes: bytes) -> Tuple[str, str]:
    try:
        from PIL import Image as PILImage
    except Exception:
        return "", "Image preview/OCR needs: pip install pillow"

    pytesseract = safe_import("pytesseract")
    if pytesseract is None:
        return "", "Image OCR needs: python -m pip install pytesseract pillow"

    tesseract_cmd = get_tesseract_cmd()
    if not tesseract_cmd:
        return "", (
            "OCR is not available in the current Streamlit process. "
            "On Fedora run: sudo dnf install tesseract tesseract-langpack-eng. "
            "Then restart Streamlit. If already installed, run: export TESSERACT_CMD=/usr/bin/tesseract before starting Streamlit."
        )

    try:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        ocr_lang, lang_note = choose_ocr_language(pytesseract)
        image = PILImage.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image, lang=ocr_lang)
        text = (text or "").strip()
        if not text:
            msg = (
                f"OCR ran using {ocr_lang}, but no readable text was detected. "
                "Try a clearer image, crop the document area, improve lighting, or paste the text manually."
            )
            if lang_note:
                msg += " " + lang_note
            return "", msg
        if lang_note:
            return text, lang_note
        return text, ""
    except Exception as exc:
        return "", f"Could not OCR image with Tesseract at {tesseract_cmd}: {exc}"


def extract_text_from_upload(uploaded_file) -> Tuple[str, str]:
    file_bytes = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    mime = uploaded_file.type or ""
    if name.endswith(".txt") or mime.startswith("text/"):
        return file_bytes.decode("utf-8", errors="ignore"), ""
    if name.endswith(".pdf") or mime == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    if name.endswith((".png", ".jpg", ".jpeg", ".webp", ".tiff")) or mime.startswith("image/"):
        return extract_text_from_image(file_bytes)
    return "", "Unsupported file type. Please upload TXT, PDF, DOCX, PNG, JPG, JPEG, WEBP, or TIFF."


# -----------------------------
# Language strings
# -----------------------------
UI = {
    "English": {
        "subtitle": "AI-assisted customs document checker for importers, exporters, and customs brokers",
        "warning": "Demo only: this tool supports document review and checklist preparation. It does not replace a licensed customs broker, customs authority, legal advisor, or tax advisor.",
        "settings": "Review settings",
        "language": "Language / Langue / اللغة",
        "shipment_type": "Shipment type",
        "origin": "Origin country",
        "destination": "Destination country",
        "documents": "Documents included",
        "input_method": "Document input method",
        "input_upload": "Upload files",
        "input_camera": "Take a picture",
        "input_paste": "Paste text manually",
        "upload": "Upload customs documents",
        "camera": "Open camera only when you need to take a picture",
        "paste": "Paste or edit extracted document text",
        "review": "Review document",
        "need_text": "Please upload a file, take a picture, or paste document text first.",
        "extracted": "Extracted text from files/camera",
        "risk_level": "Risk level",
        "risk_score": "Risk score",
        "hs_detected": "Detected HS codes",
        "detected_fields": "Detected fields",
        "missing": "Missing / unclear fields",
        "flags": "Risk flags",
        "codes_amounts": "Extracted HS codes and amounts",
        "questions": "Questions to ask the customer",
        "next_steps": "Suggested next steps",
        "download": "Download report",
        "ocr_note": "For scanned PDFs/images, OCR quality depends on the OCR engine. In production, connect this to a vision-capable AI model.",
    },
    "Français": {
        "subtitle": "Assistant IA pour vérifier les documents douaniers des importateurs, exportateurs et commissionnaires en douane",
        "warning": "Démo uniquement : cet outil aide à la revue documentaire et à la préparation de checklist. Il ne remplace pas un déclarant en douane, une autorité douanière, un conseiller juridique ou fiscal.",
        "settings": "Paramètres de revue",
        "language": "Language / Langue / اللغة",
        "shipment_type": "Type d’expédition",
        "origin": "Pays d’origine",
        "destination": "Pays de destination",
        "documents": "Documents inclus",
        "input_method": "Méthode d’entrée du document",
        "input_upload": "Téléverser des fichiers",
        "input_camera": "Prendre une photo",
        "input_paste": "Coller le texte manuellement",
        "upload": "Téléverser des documents douaniers",
        "camera": "Ouvrir la caméra uniquement si vous devez prendre une photo",
        "paste": "Coller ou modifier le texte extrait",
        "review": "Analyser le document",
        "need_text": "Veuillez téléverser un fichier, prendre une photo ou coller le texte du document.",
        "extracted": "Texte extrait des fichiers/de la caméra",
        "risk_level": "Niveau de risque",
        "risk_score": "Score de risque",
        "hs_detected": "Codes SH détectés",
        "detected_fields": "Champs détectés",
        "missing": "Champs manquants / peu clairs",
        "flags": "Alertes de risque",
        "codes_amounts": "Codes SH et montants extraits",
        "questions": "Questions à poser au client",
        "next_steps": "Prochaines étapes suggérées",
        "download": "Télécharger le rapport",
        "ocr_note": "Pour les PDF scannés/images, la qualité dépend du moteur OCR. En production, connectez cette étape à un modèle IA vision.",
    },
    "العربية": {
        "subtitle": "مساعد بالذكاء الاصطناعي لمراجعة وثائق الجمارك والاستيراد والتصدير قبل الدفع أو التقدم بالملف للجمارك",
        "warning": "نسخة تجريبية فقط: هذه الأداة تساعد في المراجعة والتحقق من نسبة صحة المعلومات المقدمة. لا تعوّض المسرح الجمركي، أو الجمارك.",
        "settings": "إعدادات المراجعة",
        "language": "Language / Langue / اللغة",
        "shipment_type": "نوع الشحنة",
        "origin": "بلد المنشأ",
        "destination": "بلد الوجهة",
        "documents": "الوثائق المرفقة",
        "input_method": "طريقة إدخال الوثيقة",
        "input_upload": "إضافة ملفات",
        "input_camera": "التقاط صورة",
        "input_paste": "لصق النص يدوياً",
        "upload": "إضافة ملفات جمركية",
        "camera": "افتح الكاميرا فقط عند الحاجة إلى التقاط صورة وتحليلها",
        "paste": "لصق أو تعديل النص المستخرج",
        "review": "مراجعة الوثيقة",
        "need_text": "يرجى إضافة ملف أو التقاط صورة أو لصق نص الوثيقة أولاً.",
        "extracted": "النص المستخرج من الملفات/الكاميرا",
        "risk_level": "مستوى المخاطر",
        "risk_score": "درجة المخاطر",
        "hs_detected": "رموز HS المكتشفة",
        "detected_fields": "الحقول المكتشفة",
        "missing": "الحقول الناقصة أو غير الواضحة",
        "flags": "مؤشرات المخاطر",
        "codes_amounts": "رموز HS والمبالغ المستخرجة",
        "questions": "أسئلة يجب طرحها على العميل",
        "next_steps": "الخطوات التالية المقترحة",
        "download": "تحميل التقرير",
        "ocr_note": "بالنسبة للصور وملفات PDF الممسوحة ضوئياً، تعتمد الجودة على محرك OCR. في النسخة الإنتاجية يمكن ربط هذه الخطوة بنموذج ذكاء اصطناعي يدعم الرؤية.",
    },
}


FIELD_LABELS = {
    "English": {"seller/exporter": "Seller / Exporter", "buyer/importer": "Buyer / Importer", "invoice number": "Invoice number", "invoice date": "Invoice date", "country of origin": "Country of origin", "HS code": "HS code", "Incoterms": "Incoterms", "currency": "Currency", "quantity": "Quantity", "net/gross weight": "Net / Gross weight"},
    "Français": {"seller/exporter": "Vendeur / Exportateur", "buyer/importer": "Acheteur / Importateur", "invoice number": "Numéro de facture", "invoice date": "Date de facture", "country of origin": "Pays d’origine", "HS code": "Code SH / HS", "Incoterms": "Incoterms", "currency": "Devise", "quantity": "Quantité", "net/gross weight": "Poids net / brut"},
    "العربية": {"seller/exporter": "البائع / المصدر", "buyer/importer": "المشتري / المستورد", "invoice number": "رقم الفاتورة", "invoice date": "تاريخ الفاتورة", "country of origin": "بلد المنشأ", "HS code": "رمز HS / البند الجمركي", "Incoterms": "شروط التسليم Incoterms", "currency": "العملة", "quantity": "الكمية", "net/gross weight": "الوزن الصافي / الإجمالي"},
}

RISK_LABELS = {
    "English": {"restricted / sensitive wording": "Restricted or sensitive wording", "vague product description": "Vague product description", "free of charge / samples": "Free of charge / samples"},
    "Français": {"restricted / sensitive wording": "Terminologie sensible ou réglementée", "vague product description": "Description produit imprécise", "free of charge / samples": "Échantillons / sans valeur commerciale"},
    "العربية": {"restricted / sensitive wording": "مصطلحات حساسة أو مقيدة", "vague product description": "وصف غير دقيق للبضاعة", "free of charge / samples": "عينات أو بدون قيمة تجارية"},
}

LOCAL_TEXT = {
    "English": {
        "none": "None", "none_detected": "None detected", "no_missing": "No major missing fields detected by the rule-based checker.", "no_flags": "No high-risk keywords detected.", "no_questions": "No immediate clarification questions generated.", "missing_col": "Missing / unclear field", "risk_area_col": "Risk area", "matched_terms_col": "Matched terms", "amounts": "Commercial amounts", "hs_codes_label": "HS codes", "hs_model": "HS/SH reference model", "hs_upload": "Upload latest HS/SH reference CSV", "hs_help": "Optional: upload a CSV with columns: code, description, keywords. If empty, the app uses the starter HS/SH sample table.", "object_match": "Manifest object-name and description check", "object_col": "Object name declared in manifest/document", "declared_desc_col": "Declared description", "hs_ref_col": "HS/SH reference description", "match_col": "Description match", "score_col": "Match score", "note_col": "Review note", "match_ok": "Likely corresponds", "match_review": "Needs manual review", "no_objects": "No manifest object names or HS/SH description pairs detected.",
        "shipment_options": ["Import", "Export", "Transit", "Unknown"], "doc_options": ["Commercial invoice", "Packing list", "Cargo manifest", "Bill of lading", "Air waybill", "Certificate of origin", "Other"], "paste_info": "Paste the document text below, then run the review.", "placeholder": "Paste extracted document text here...", "ocr_engine_missing": "OCR engine not found. Images/photos need Tesseract or a future AI vision model.",
        "next_steps_list": ["Ask the customer for missing or unclear information.", "Validate HS classification with a qualified customs professional.", "Confirm destination-country import requirements, restrictions, duties, and taxes.", "Keep the review report with the shipment file for audit traceability."],
        "questions": {"hs": "Confirm product function, material, end use, and proposed HS code.", "origin": "Confirm the country of origin for each line item.", "incoterms": "Confirm the agreed Incoterms and named place, e.g. FCA Tunis or DAP Prague.", "weight": "Confirm net and gross weight for the shipment or each line item.", "vague": "Replace generic product descriptions with precise commercial descriptions."},
    },
    "Français": {
        "none": "Aucun", "none_detected": "Aucun détecté", "no_missing": "Aucun champ majeur manquant détecté par le contrôle basé sur des règles.", "no_flags": "Aucun mot-clé à haut risque détecté.", "no_questions": "Aucune question immédiate générée.", "missing_col": "Champ manquant / peu clair", "risk_area_col": "Zone de risque", "matched_terms_col": "Termes détectés", "amounts": "Montants commerciaux", "hs_codes_label": "Codes HS/SH", "hs_model": "Modèle de référence HS/SH", "hs_upload": "Téléverser le dernier fichier de référence HS/SH CSV", "hs_help": "Optionnel : CSV avec colonnes : code, description, keywords. Si vide, l’application utilise une table d’exemple HS/SH.", "object_match": "Contrôle du nom d’objet déclaré dans le manifeste et de la description", "object_col": "Nom d’objet déclaré dans le manifeste/document", "declared_desc_col": "Description déclarée", "hs_ref_col": "Description de référence HS/SH", "match_col": "Correspondance de la description", "score_col": "Score", "note_col": "Note de revue", "match_ok": "Correspond probablement", "match_review": "Revue manuelle requise", "no_objects": "Aucun nom d’objet manifeste ou couple description HS/SH détecté.",
        "shipment_options": ["Import", "Export", "Transit", "Inconnu"], "doc_options": ["Facture commerciale", "Liste de colisage", "Manifeste cargo", "Connaissement", "Lettre de transport aérien", "Certificat d’origine", "Autre"], "paste_info": "Collez le texte du document ci-dessous, puis lancez l’analyse.", "placeholder": "Collez ici le texte extrait du document...", "ocr_engine_missing": "Moteur OCR introuvable. Les images/photos nécessitent Tesseract ou un futur modèle IA vision.",
        "next_steps_list": ["Demander au client les informations manquantes ou peu claires.", "Valider la classification HS/SH avec un professionnel qualifié en douane.", "Confirmer les exigences d’importation du pays de destination, les restrictions, droits et taxes.", "Conserver le rapport de revue avec le dossier d’expédition pour la traçabilité."],
        "questions": {"hs": "Confirmer la fonction du produit, sa matière, son usage final et le code HS/SH proposé.", "origin": "Confirmer le pays d’origine pour chaque ligne d’article.", "incoterms": "Confirmer l’Incoterm convenu et le lieu nommé, par exemple FCA Tunis ou DAP Prague.", "weight": "Confirmer le poids net et brut de l’expédition ou de chaque ligne.", "vague": "Remplacer les descriptions génériques par des descriptions commerciales précises."},
    },
    "العربية": {
        "none": "لا يوجد", "none_detected": "لم يتم العثور على شيء", "no_missing": "لم يتم اكتشاف حقول أساسية ناقصة بواسطة الفحص المبني على القواعد.", "no_flags": "لم يتم اكتشاف كلمات ذات مخاطر عالية.", "no_questions": "لم يتم إنشاء أسئلة توضيحية حالياً.", "missing_col": "الحقل الناقص أو غير الواضح", "risk_area_col": "مجال الخطر", "matched_terms_col": "الكلمات المطابقة", "amounts": "المبالغ التجارية", "hs_codes_label": "رموز HS", "hs_model": "نموذج مرجع HS/SH", "hs_upload": "رفع ملف CSV لأحدث مرجع HS/SH", "hs_help": "اختياري: ارفع ملف CSV يحتوي على الأعمدة: code, description, keywords. إذا لم يتم الرفع، سيستخدم التطبيق جدولاً تجريبياً مرفقاً.", "object_match": "التحقق من اسم البضاعة المصرح به في المانيفست ومطابقته للوصف", "object_col": "اسم البضاعة المصرح به في المانيفست/الوثيقة", "declared_desc_col": "الوصف المصرح به", "hs_ref_col": "وصف مرجع HS/SH", "match_col": "مطابقة الوصف", "score_col": "درجة المطابقة", "note_col": "ملاحظة المراجعة", "match_ok": "غالباً متطابق", "match_review": "يتطلب مراجعة يدوية", "no_objects": "لم يتم اكتشاف أسماء بضائع أو أزواج وصف ورمز HS/SH.",
        "shipment_options": ["استيراد", "تصدير", "عبور", "غير معروف"], "doc_options": ["فاتورة", "وثيقة في بيان الشحنة", "سند الشحن البحري", "سند الشحن الجوي", "شهادة في المنشأ", "أخرى"], "paste_info": "ألصق نص الوثيقة أدناه ثم شغّل المراجعة.", "placeholder": "ألصق النص المستخرج من الوثيقة هنا...", "ocr_engine_missing": "لم يتم العثور على محرك OCR. الصور تحتاج إلى Tesseract أو لاحقاً إلى نموذج ذكاء اصطناعي يدعم الرؤية.",
        "next_steps_list": ["اطلب من العميل المعلومات الناقصة أو غير الواضحة.", "تحقق من تصنيف HS مع مختص أو مخلص جمركي مؤهل.", "أكد متطلبات الاستيراد في بلد الوجهة، والقيود، والرسوم، والضرائب.", "احتفظ بتقرير المراجعة مع ملف الشحنة لضمان التتبع والتدقيق."],
        "questions": {"hs": "تأكيد وظيفة المنتج، والمادة المصنوع منها، والاستخدام النهائي، ورمز HS المقترح.", "origin": "تأكيد بلد المنشأ لكل بند من البضائع.", "incoterms": "تأكيد شروط Incoterms المتفق عليها والمكان المحدد، مثل FCA Tunis أو DAP Prague.", "weight": "تأكيد الوزن الصافي والإجمالي للشحنة أو لكل بند.", "vague": "استبدال الوصف العام للبضاعة بوصف تجاري دقيق وواضح."},
    },
}

REQUIRED_FIELDS = {
    "seller/exporter": ["seller", "exporter", "shipper", "vendeur", "exportateur", "المصدر", "البائع"],
    "buyer/importer": ["buyer", "importer", "consignee", "acheteur", "importateur", "المستورد", "المشتري"],
    "invoice number": ["invoice no", "invoice number", "invoice #", "facture", "رقم الفاتورة"],
    "invoice date": ["invoice date", "date", "تاريخ الفاتورة"],
    "country of origin": ["country of origin", "origin", "origine", "pays d'origine", "بلد المنشأ", "المنشأ"],
    "HS code": ["hs code", "hscode", "tariff code", "commodity code", "code sh", "code hs", "رمز hs", "البند الجمركي"],
    "Incoterms": ["incoterms", "exw", "fca", "cpt", "cip", "dap", "dpu", "ddp", "fas", "fob", "cfr", "cif"],
    "currency": ["eur", "usd", "gbp", "czk", "aed", "tnd", "currency", "devise", "عملة"],
    "quantity": ["quantity", "qty", "pcs", "units", "quantité", "كمية", "عدد"],
    "net/gross weight": ["net weight", "gross weight", "kg", "weight", "poids", "الوزن", "كغ"],
}

RISK_KEYWORDS = {
    "restricted / sensitive wording": ["military", "dual-use", "weapon", "chemical", "medical", "pharmaceutical", "battery", "lithium", "radio", "encryption", "militaire", "chimique", "batterie", "دواء", "بطارية", "ليثيوم", "عسكري"],
    "vague product description": ["goods", "items", "parts", "samples", "miscellaneous", "general merchandise", "marchandises", "articles", "pièces", "échantillons", "بضائع", "قطع", "عينات"],
    "free of charge / samples": ["free of charge", "sample", "no commercial value", "sans valeur commerciale", "gratuit", "بدون قيمة تجارية", "عينة"],
}


def contains_any(text: str, terms: List[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def extract_amounts(text: str) -> List[str]:
    """Extract likely commercial monetary amounts only, not every number."""
    patterns = [
        r"\b(?:EUR|USD|GBP|CZK|AED|TND)\s*[:]?\s*\d{1,3}(?:[,. ]\d{3})*(?:[,.]\d{2})?\b",
        r"\b\d{1,3}(?:[,. ]\d{3})*(?:[,.]\d{2})?\s*(?:EUR|USD|GBP|CZK|AED|TND)\b",
        r"[€$£]\s*\d{1,3}(?:[,. ]\d{3})*(?:[,.]\d{2})?\b",
        r"\b(?:total|amount|value|subtotal|montant|valeur|المبلغ|الإجمالي|القيمة)\s*[:\-]?\s*(?:EUR|USD|GBP|CZK|AED|TND|€|\$|£)?\s*\d{1,3}(?:[,. ]\d{3})*(?:[,.]\d{2})?\b",
    ]
    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, re.IGNORECASE))
    cleaned = []
    for item in found:
        value = item.strip()
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned[:20]


def extract_hs_codes(text: str) -> List[str]:
    """Extract likely HS/SH codes without confusing dates or invoice IDs as HS codes."""
    candidates = []
    explicit_pattern = r"(?i)(?:HS\s*(?:code)?|H\.S\.|code\s*SH|code\s*HS|tariff\s*(?:code)?|commodity\s*code|رمز\s*HS|البند\s*الجمركي)\s*[:#\-]?\s*([0-9]{4}(?:[\.\s]?[0-9]{2}){0,3})"
    candidates.extend(re.findall(explicit_pattern, text))
    dotted_pattern = r"\b([0-9]{4}\.[0-9]{2}(?:\.[0-9]{2,4})?)\b"
    candidates.extend(re.findall(dotted_pattern, text))
    normalized = []
    for code in candidates:
        c = re.sub(r"\s+", "", code.strip()).replace("-", ".")
        if re.match(r"^(19|20)\d{2}[\-.]", c):
            continue
        digits = re.sub(r"\D", "", c)
        if 4 <= len(digits) <= 10 and c not in normalized:
            normalized.append(c)
    return normalized



# -----------------------------
# HS/SH reference and manifest/object matching
# -----------------------------
STARTER_HS_REFERENCE = [
    {"code": "6109.10", "description": "T-shirts, singlets and other vests, knitted or crocheted, of cotton", "keywords": "t-shirt tshirt shirt vest cotton coton coton t shirts vêtements vetements"},
    {"code": "6203.42", "description": "Men's or boys' trousers, bib and brace overalls, breeches and shorts, of cotton", "keywords": "trousers pants pantalons cotton coton vêtements vetements"},
    {"code": "6204.62", "description": "Women's or girls' trousers, bib and brace overalls, breeches and shorts, of cotton", "keywords": "trousers pants pantalons cotton coton women girls vêtements vetements"},
    {"code": "8483.90", "description": "Parts suitable for use solely or principally with transmission shafts, gears, gear boxes and other articles of heading 8483", "keywords": "parts pieces pièces détachées mecaniques mécaniques mechanical spare gears shafts transmission gearboxes non dangereuses"},
    {"code": "8708.99", "description": "Parts and accessories of motor vehicles", "keywords": "auto parts vehicle spare pièces automobile véhicules"},
    {"code": "8517.13", "description": "Smartphones for wireless networks", "keywords": "smartphone phone mobile telephone téléphone"},
    {"code": "9403.60", "description": "Wooden furniture", "keywords": "furniture wood wooden meubles bois"},
]


def normalize_code(code: str) -> str:
    code = str(code or "").strip()
    code = code.replace(" ", "").replace("-", ".")
    # keep common HS punctuation but remove duplicate dots
    code = re.sub(r"[^0-9.]", "", code)
    return code.strip(".")


def load_hs_reference(uploaded_csv=None) -> List[Dict[str, str]]:
    """Load a user-supplied HS/SH reference CSV or fallback to the starter table.

    Expected CSV columns: code, description, keywords. The keywords column is optional.
    This is not an official tariff database; it is a replaceable reference layer for the prototype.
    """
    if uploaded_csv is not None:
        try:
            df = pd.read_csv(uploaded_csv)
            lower_cols = {str(c).strip().lower(): c for c in df.columns}
            code_col = lower_cols.get("code") or lower_cols.get("hs_code") or lower_cols.get("hs") or lower_cols.get("sh")
            desc_col = lower_cols.get("description") or lower_cols.get("desc") or lower_cols.get("designation")
            kw_col = lower_cols.get("keywords") or lower_cols.get("keyword") or lower_cols.get("mots_cles")
            if code_col and desc_col:
                rows = []
                for _, row in df.iterrows():
                    code = normalize_code(row.get(code_col, ""))
                    desc = str(row.get(desc_col, "")).strip()
                    kws = str(row.get(kw_col, "") if kw_col else "").strip()
                    if code and desc:
                        rows.append({"code": code, "description": desc, "keywords": kws})
                if rows:
                    return rows
        except Exception:
            pass
    return STARTER_HS_REFERENCE


def find_hs_reference(hs_code: str, hs_reference: List[Dict[str, str]]) -> Dict[str, str]:
    code = normalize_code(hs_code)
    if not code:
        return {}
    # Prefer exact match, then longest prefix match.
    for row in hs_reference:
        if normalize_code(row.get("code")) == code:
            return row
    digits = re.sub(r"\D", "", code)
    best = {}
    best_len = 0
    for row in hs_reference:
        row_code = normalize_code(row.get("code"))
        row_digits = re.sub(r"\D", "", row_code)
        common = 0
        for a, b in zip(digits, row_digits):
            if a == b:
                common += 1
            else:
                break
        if common >= 4 and common > best_len:
            best = row
            best_len = common
    return best


def tokenize_for_match(value: str) -> set:
    value = (value or "").lower()
    value = re.sub(r"[^a-z0-9À-ÿ\u0600-\u06FF]+", " ", value)
    stop = {"the", "and", "or", "of", "for", "with", "other", "articles", "goods", "items", "de", "des", "du", "la", "le", "les", "et", "en", "pour", "avec", "من", "في", "و", "أو", "على"}
    return {x for x in value.split() if len(x) > 2 and x not in stop}


def similarity_score(a: str, b: str) -> int:
    ta = tokenize_for_match(a)
    tb = tokenize_for_match(b)
    if not ta or not tb:
        return 0
    return int(round(100 * len(ta & tb) / max(1, len(ta | tb))))


def clean_manifest_description(line: str) -> str:
    line = re.sub(r"(?i)(hs\s*code|code\s*hs|code\s*sh|tariff\s*code|commodity\s*code)\s*[:#\-]?", " ", line)
    line = re.sub(r"\b[0-9]{4}\.[0-9]{2}(?:\.[0-9]{2,4})?\b", " ", line)
    line = re.sub(r"\b[0-9]{4}\s*/\s*\b", " ", line)
    line = re.sub(r"\b\d+\s*(cartons?|boxes|pcs|kg|cbm|eur|usd|tnd|aed)\b", " ", line, flags=re.I)
    line = re.sub(r"\s+", " ", line).strip(" -:/|,")
    return line.strip()


def extract_manifest_items(text: str) -> List[Dict[str, str]]:
    """Extract likely object names declared in a cargo manifest or invoice lines.

    The goal is not final classification, but a practical pre-check: object name/description vs HS/SH code.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    items = []
    for idx, line in enumerate(lines):
        codes = extract_hs_codes(line)
        if not codes and idx + 1 < len(lines):
            # Common OCR layout: description line followed by a line with HS code.
            next_codes = extract_hs_codes(lines[idx + 1])
            if next_codes:
                codes = next_codes
        if codes:
            context_parts = []
            if idx > 0:
                context_parts.append(lines[idx - 1])
            context_parts.append(line)
            if idx + 1 < len(lines) and not re.search(r"\b(container|seal|mrsu|cmau|sealu|invoice|date)\b", lines[idx + 1], re.I):
                context_parts.append(lines[idx + 1])
            desc = clean_manifest_description(" / ".join(context_parts))
            if not desc or len(desc) < 3:
                desc = clean_manifest_description(line)
            for code in codes:
                pair = {"object_name": desc, "declared_description": desc, "hs_code": normalize_code(code)}
                if pair not in items:
                    items.append(pair)
    # Fallback: detect lines after manifest/product description labels even if HS missing.
    if not items:
        for line in lines:
            if re.search(r"(?i)(description|goods|marchandise|désignation|designation|object|article|commodity|البضاعة|الوصف)", line):
                desc = clean_manifest_description(line)
                if desc:
                    items.append({"object_name": desc, "declared_description": desc, "hs_code": ""})
    return items[:30]




def _clean_desc_fragment(value: str) -> str:
    """Clean table-cell text while keeping the real commercial description."""
    value = re.sub(r"\s+", " ", value or "").strip(" /|-:,;")
    # Remove common transport identifiers accidentally captured before the description.
    value = re.sub(r"(?i)^.*?(?:SEAL\s*\d+|SEAL[0-9A-Z]+)\s+", "", value)
    value = re.sub(r"(?i)^.*?(?:Description\s*marchandises?|Description\s*goods?)\s+", "", value)
    value = re.sub(r"\b[0-9]{4}\.[0-9]{2}(?:\s*/\s*[0-9]{4}\.[0-9]{2})*\b.*$", "", value).strip(" /|-:,;")
    return value


def extract_manifest_line_items(text: str, hs_reference: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Extract manifest cargo rows with description, HS codes, value, packages, weight, volume, and origin.

    This parser is intentionally conservative. It first looks for cargo-manifest table rows like:
    SEAL987654 Vêtements ... 6109.10 / 6203.42 150 cartons 1,250 kg 12 CBM 12,700 EUR France / UE
    and then falls back to nearby-line matching.
    """
    flat = re.sub(r"[\u2019’]", "'", text or "")
    flat = re.sub(r"\s+", " ", flat).strip()
    rows = []

    # Main cargo-manifest pattern, works with text extracted from the sample manifest PDF.
    row_pattern = re.compile(
        r"(?P<bl>MRSRAD\s*\d{4,}\s*\d{0,3}|[A-Z]{2,}\s*\d{3,}\s*\d{0,3})\s+"
        r"(?P<container>[A-Z]{4}\d{5,}\s*(?:/|\d|\s|'|DRY|HIGH|CUBE|REEFER|HC|GP|\u2019|’)+?)\s+"
        r"(?P<seal>SEAL\s*[0-9A-Z]+)\s+"
        r"(?P<description>.+?)\s+"
        r"(?P<codes>\d{4}\.\d{2}(?:\s*/\s*\d{4}\.\d{2})*)\s+"
        r"(?P<packages>\d+\s+(?:cartons?|palettes?|boxes?|colis|packages?))\s+"
        r"(?P<weight>[\d,. ]+\s*kg)\s+"
        r"(?P<volume>[\d,. ]+\s*CBM)\s+"
        r"(?P<value>[\d,. ]+\s*(?:EUR|USD|TND|AED|GBP|CZK))\s+"
        r"(?P<origin>(?:France\s*/\s*UE|[A-Za-zÀ-ÿ ]{2,30}))",
        re.IGNORECASE,
    )

    for m in row_pattern.finditer(flat):
        desc = _clean_desc_fragment(m.group("description"))
        codes = [normalize_code(c) for c in re.findall(r"\d{4}\.\d{2}(?:\.\d{2,4})?", m.group("codes"))]
        line_id = re.sub(r"\s+", "", m.group("bl"))
        base = {
            "line_id": line_id,
            "container": re.sub(r"\s+", " ", m.group("container")).strip(),
            "seal": re.sub(r"\s+", "", m.group("seal")),
            "declared_description": desc,
            "packages": re.sub(r"\s+", " ", m.group("packages")).strip(),
            "weight": re.sub(r"\s+", " ", m.group("weight")).strip(),
            "volume": re.sub(r"\s+", " ", m.group("volume")).strip(),
            "declared_value": re.sub(r"\s+", " ", m.group("value")).strip(),
            "origin": re.sub(r"\s+", " ", m.group("origin")).strip(),
        }
        for code in codes:
            ref = find_hs_reference(code, hs_reference)
            rows.append({**base, "hs_code": code, "hs_reference_description": ref.get("description", "")})

    # Fallback for less structured OCR: group nearby description, HS code, and monetary value.
    if not rows:
        lines = [re.sub(r"\s+", " ", l).strip() for l in (text or "").splitlines() if l.strip()]
        for idx, line in enumerate(lines):
            codes = extract_hs_codes(line)
            if not codes and idx + 1 < len(lines):
                codes = extract_hs_codes(lines[idx + 1])
            if not codes:
                continue
            window = " / ".join(lines[max(0, idx-3): min(len(lines), idx+4)])
            desc = _clean_desc_fragment(window)
            amount_match = re.search(r"\b[\d,. ]+\s*(?:EUR|USD|TND|AED|GBP|CZK)\b", window, re.I)
            value = amount_match.group(0).strip() if amount_match else ""
            for code in codes:
                ref = find_hs_reference(code, hs_reference)
                rows.append({
                    "line_id": "Detected line",
                    "container": "",
                    "seal": "",
                    "declared_description": desc,
                    "packages": "",
                    "weight": "",
                    "volume": "",
                    "declared_value": value,
                    "origin": "",
                    "hs_code": normalize_code(code),
                    "hs_reference_description": ref.get("description", ""),
                })

    # Deduplicate.
    deduped = []
    seen = set()
    for row in rows:
        key = (row.get("line_id"), row.get("declared_description"), row.get("hs_code"), row.get("declared_value"))
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped[:50]


def extract_commercial_amount_details(text: str, manifest_items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Return meaningful amount rows instead of raw number fragments."""
    rows = []
    seen = set()
    for item in manifest_items:
        value = item.get("declared_value", "")
        desc = item.get("declared_description", "")
        if value and (item.get("line_id"), value) not in seen:
            seen.add((item.get("line_id"), value))
            rows.append({
                "Amount": value,
                "Meaning": f"Declared value for {desc}" if desc else "Declared line value",
                "Line / Object": item.get("line_id", ""),
            })
    total_match = re.search(r"(?i)(?:Valeur totale déclarée|Total declared value|Total value|Valeur totale|القيمة الإجمالية)\s*[:\-]?\s*([\d,. ]+\s*(?:EUR|USD|TND|AED|GBP|CZK))", text or "")
    if total_match:
        total_value = re.sub(r"\s+", " ", total_match.group(1)).strip()
        rows.append({"Amount": total_value, "Meaning": "Total declared manifest value", "Line / Object": "Manifest total"})
    if not rows:
        for amount in extract_amounts(text):
            rows.append({"Amount": amount, "Meaning": "Possible commercial amount detected near currency/amount keyword", "Line / Object": "Document"})
    return rows[:30]


def build_hs_details(manifest_items: List[Dict[str, str]], hs_codes: List[str], hs_reference: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Build a clear HS table: code -> reference meaning -> declared object/value."""
    rows = []
    if manifest_items:
        for item in manifest_items:
            code = item.get("hs_code", "")
            ref_desc = item.get("hs_reference_description") or find_hs_reference(code, hs_reference).get("description", "")
            rows.append({
                "HS/SH code": code,
                "Reference meaning": ref_desc or "Code not found in uploaded HS/SH reference",
                "Declared object / description": item.get("declared_description", ""),
                "Declared value": item.get("declared_value", ""),
                "Line / B/L": item.get("line_id", ""),
            })
    else:
        for code in hs_codes:
            ref = find_hs_reference(code, hs_reference)
            rows.append({
                "HS/SH code": code,
                "Reference meaning": ref.get("description", "Code not found in uploaded HS/SH reference"),
                "Declared object / description": "Not linked to a specific manifest line",
                "Declared value": "",
                "Line / B/L": "Document",
            })
    return rows

def check_manifest_description_matches(text: str, hs_reference: List[Dict[str, str]], lang: str) -> List[Dict[str, str]]:
    lt = LOCAL_TEXT[lang]
    rows = []
    manifest_items = extract_manifest_line_items(text, hs_reference)
    if manifest_items:
        for item in manifest_items:
            hs_code = item.get("hs_code", "")
            ref_desc = item.get("hs_reference_description", "")
            ref_keywords = find_hs_reference(hs_code, hs_reference).get("keywords", "") if hs_code else ""
            declared = item.get("declared_description", "")
            score = max(similarity_score(declared, ref_desc), similarity_score(declared, ref_keywords)) if ref_desc else 0
            if not hs_code:
                status = lt["match_review"]
                note = "No HS/SH code found for this item."
            elif not ref_desc:
                status = lt["match_review"]
                note = "HS/SH code is not found in the loaded reference table. Upload a fuller HS/SH reference CSV."
            elif score >= 18:
                status = lt["match_ok"]
                note = "Declared item wording corresponds to the loaded HS/SH reference. Final classification must still be validated by a customs professional."
            else:
                status = lt["match_review"]
                note = "Declared item wording has weak overlap with the HS/SH reference description. Review the description, material, function, and exact HS classification."
            rows.append({
                lt["object_col"]: declared,
                "HS/SH": hs_code or lt["none_detected"],
                "Declared value": item.get("declared_value", ""),
                "Packages / Weight / Volume": " / ".join(x for x in [item.get("packages", ""), item.get("weight", ""), item.get("volume", "")] if x),
                lt["hs_ref_col"]: ref_desc or lt["none_detected"],
                lt["match_col"]: status,
                lt["score_col"]: score,
                lt["note_col"]: note,
            })
        return rows

    # Fallback to the previous generic detection logic when no structured manifest row is found.
    for item in extract_manifest_items(text):
        hs_code = item.get("hs_code", "")
        ref = find_hs_reference(hs_code, hs_reference) if hs_code else {}
        ref_desc = ref.get("description", "")
        ref_keywords = ref.get("keywords", "")
        score = max(similarity_score(item.get("declared_description", ""), ref_desc), similarity_score(item.get("declared_description", ""), ref_keywords)) if ref else 0
        if not hs_code:
            status = lt["match_review"]
            note = "No HS/SH code found for this object name."
        elif not ref:
            status = lt["match_review"]
            note = "HS/SH code not found in the loaded reference table. Upload a fuller HS/SH reference CSV."
        elif score >= 18:
            status = lt["match_ok"]
            note = "Declared object wording has overlap with the HS/SH reference description."
        else:
            status = lt["match_review"]
            note = "Declared object wording has weak overlap with the HS/SH reference description."
        rows.append({
            lt["object_col"]: item.get("object_name", ""),
            "HS/SH": hs_code or lt["none_detected"],
            lt["declared_desc_col"]: item.get("declared_description", ""),
            lt["hs_ref_col"]: ref_desc or lt["none_detected"],
            lt["match_col"]: status,
            lt["score_col"]: score,
            lt["note_col"]: note,
        })
    return rows

def review_document(text: str, lang: str = "English", hs_reference: List[Dict[str, str]] = None) -> Dict:
    missing, present = [], []
    for field, terms in REQUIRED_FIELDS.items():
        if contains_any(text, terms):
            present.append(field)
        else:
            missing.append(field)

    flags = []
    for label, terms in RISK_KEYWORDS.items():
        matched = [t for t in terms if t.lower() in text.lower()]
        if matched:
            flags.append({"risk_key": label, "matched_terms": ", ".join(sorted(set(matched)))})

    hs_reference = hs_reference or STARTER_HS_REFERENCE
    hs_codes = extract_hs_codes(text)
    manifest_items = extract_manifest_line_items(text, hs_reference)
    # Prefer HS codes that are linked to manifest rows; fall back to generic document-level detection.
    if manifest_items:
        hs_codes = []
        for item in manifest_items:
            code = item.get("hs_code")
            if code and code not in hs_codes:
                hs_codes.append(code)
    amounts = extract_amounts(text)
    amount_details = extract_commercial_amount_details(text, manifest_items)
    hs_details = build_hs_details(manifest_items, hs_codes, hs_reference)

    risk_score = len(missing) * 8 + len(flags) * 12
    if not hs_codes:
        risk_score += 20
    if "country of origin" in missing:
        risk_score += 12
    risk_score = min(risk_score, 100)

    risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 65 else "High"

    questions = []
    q = LOCAL_TEXT[lang]["questions"]
    if "HS code" in missing or not hs_codes:
        questions.append(q["hs"])
    if "country of origin" in missing:
        questions.append(q["origin"])
    if "Incoterms" in missing:
        questions.append(q["incoterms"])
    if "net/gross weight" in missing:
        questions.append(q["weight"])
    if any("vague" in f["risk_key"] for f in flags):
        questions.append(q["vague"])

    object_matches = check_manifest_description_matches(text, hs_reference, lang)
    return {"present": present, "missing": missing, "flags": flags, "hs_codes": hs_codes, "hs_details": hs_details, "amounts": amounts, "amount_details": amount_details, "object_matches": object_matches, "risk_score": risk_score, "risk_level": risk_level, "questions": questions}


# -----------------------------
# Interactive HS/SH classification flow
# -----------------------------

def official_chapter_for_code(code: str) -> str:
    """Return the official HS chapter label for an HS/SH code."""
    chap = chapter_number_from_code_or_label(code)
    return CHAPTER_TO_LABEL.get(chap, f"Chapter {chap} - Uploaded reference" if chap else "Uploaded reference chapter")


HS_CLASSIFICATION_TREE = [
    {
        "section": "Section XX - Miscellaneous manufactured articles",
        "chapter": "Chapter 94 - Furniture; bedding; lamps; prefabricated buildings",
        "heading": "9401 - Seats, whether or not convertible into beds, and parts thereof",
        "subheading": "9401.79 - Seats with metal frames, other",
        "code": "9401.79",
        "description": "Seats and chairs, other than medical/dental/barber chairs, with metal frames",
        "keywords": "chair chairs seat seats chaise chaises كرسي كراسي furniture sitting metal frame",
        "checks": [
            "The product is a seat/chair, not a vehicle seat or medical/dental/barber chair.",
            "The material/frame type was checked.",
            "The product is not more specifically covered by another 9401 subheading.",
        ],
    },
    {
        "section": "Section XVIII - Optical, photographic, medical instruments; clocks; musical instruments",
        "chapter": "Chapter 90 - Optical, photographic, measuring, medical instruments",
        "heading": "9004 - Spectacles, goggles and the like, corrective, protective or other",
        "subheading": "9004.90 - Spectacles, goggles and the like, other",
        "code": "9004.90",
        "description": "Spectacles, goggles and similar eyewear",
        "keywords": "glasses spectacles goggles eyewear lunettes نظارات protective corrective optical",
        "checks": [
            "The product is eyewear such as spectacles, goggles, or similar articles.",
            "The purpose was checked: corrective, protective, sunglasses, or other.",
            "The product is not only lenses or frames classified separately.",
        ],
    },
    {
        "section": "Section XVII - Vehicles, aircraft, vessels and transport equipment",
        "chapter": "Chapter 87 - Vehicles other than railway or tramway rolling-stock",
        "heading": "8712 - Bicycles and other cycles, not motorised",
        "subheading": "8712.00 - Bicycles and other cycles, not motorised",
        "code": "8712.00",
        "description": "Bicycles and other cycles, not motorised",
        "keywords": "bicycle bicycles bike bikes cycle cycles vélo velos bicyclette دراجة",
        "checks": [
            "The product is a bicycle or non-motorised cycle.",
            "It is not a motorcycle, e-bike classified elsewhere, or vehicle part.",
            "The product is complete, not only a bicycle part/accessory.",
        ],
    },
    {
        "section": "Section XX - Miscellaneous manufactured articles",
        "chapter": "Chapter 96 - Miscellaneous manufactured articles",
        "heading": "9608 - Ball point pens; felt tipped and other porous-tipped pens; fountain pens; markers",
        "subheading": "9608.10 - Ball point pens",
        "code": "9608.10",
        "description": "Ball point pens",
        "keywords": "pen pens ballpoint ball point stylo stylos قلم أقلام writing instrument",
        "checks": [
            "The product is a pen or writing instrument.",
            "The exact pen type was checked: ball point, felt-tip, fountain, marker, or other.",
            "The product is not only a refill, nib, or separate part.",
        ],
    },
    {
        "section": "Section XIII - Articles of stone, plaster, cement, ceramic, glass",
        "chapter": "Chapter 70 - Glass and glassware",
        "heading": "7013 - Glassware of a kind used for table, kitchen, toilet, office, indoor decoration or similar purposes",
        "subheading": "7013.37 - Drinking glasses, other than of glass-ceramics",
        "code": "7013.37",
        "description": "Drinking glasses, other than of glass-ceramics",
        "keywords": "drinking glass drinking glasses glassware cup cups verre verres كؤوس كأس كوب زجاج",
        "checks": [
            "The product is glassware, not optical glasses or spectacles.",
            "The use was checked: drinking/table/kitchen/decoration/office.",
            "The material was checked: glass, not plastic, ceramic, or metal.",
        ],
    },

    {
        "section": "Section XI - Textiles and textile articles",
        "chapter": "Chapter 61 - Articles of apparel and clothing accessories, knitted or crocheted",
        "heading": "6109 - T-shirts, singlets and other vests, knitted or crocheted",
        "subheading": "6109.10 - Of cotton",
        "code": "6109.10",
        "description": "T-shirts, singlets and other vests, knitted or crocheted, of cotton",
        "keywords": "t-shirt tshirt shirt vest cotton coton knitted crocheted vêtement vêtements coton tee-shirt",
        "checks": [
            "The product is a T-shirt, singlet, vest, or similar upper-body garment.",
            "The product is knitted or crocheted, not woven.",
            "The main material is cotton.",
        ],
    },
    {
        "section": "Section XI - Textiles and textile articles",
        "chapter": "Chapter 62 - Articles of apparel and clothing accessories, not knitted or crocheted",
        "heading": "6203 - Men's or boys' suits, trousers, shorts and similar garments",
        "subheading": "6203.42 - Trousers, bib and brace overalls, breeches and shorts, of cotton",
        "code": "6203.42",
        "description": "Men's or boys' trousers, bib and brace overalls, breeches and shorts, of cotton",
        "keywords": "trousers pants pantalons cotton coton woven men boys shorts breeches",
        "checks": [
            "The product is trousers, pants, shorts, or similar lower-body garment.",
            "The product is woven, not knitted/crocheted.",
            "The main material is cotton.",
            "The garment is for men or boys, or the documents do not clearly indicate women/girls.",
        ],
    },
    {
        "section": "Section XVI - Machinery and mechanical/electrical equipment",
        "chapter": "Chapter 84 - Nuclear reactors, boilers, machinery and mechanical appliances",
        "heading": "8483 - Transmission shafts, gears, gear boxes and related parts",
        "subheading": "8483.90 - Parts",
        "code": "8483.90",
        "description": "Parts suitable for use solely or principally with transmission shafts, gears, gear boxes and other articles of heading 8483",
        "keywords": "mechanical parts spare parts pieces pièces détachées gears shafts transmission gearboxes mecaniques mécaniques",
        "checks": [
            "The item is a mechanical part, not a complete machine.",
            "The part is for shafts, gears, gearboxes, clutches, or transmission components.",
            "The part is not more specifically described under another heading.",
        ],
    },
    {
        "section": "Section XVII - Vehicles, aircraft, vessels and transport equipment",
        "chapter": "Chapter 87 - Vehicles other than railway or tramway rolling-stock",
        "heading": "8703 - Motor cars and other motor vehicles principally designed for the transport of persons",
        "subheading": "8703.23 - Vehicles with spark-ignition engine, cylinder capacity over 1,500 cc but not over 3,000 cc",
        "code": "8703.23",
        "description": "Motor cars and other motor vehicles principally designed for the transport of persons",
        "keywords": "car cars vehicle vehicles voiture automobile passenger motor car moteur transport persons",
        "checks": [
            "The product is a complete motor car/passenger vehicle, not only a spare part.",
            "The vehicle is principally designed for transport of persons.",
            "Engine/fuel type and cylinder capacity were checked for the final national tariff subheading.",
        ],
    },
    {
        "section": "Section XVII - Vehicles, aircraft, vessels and transport equipment",
        "chapter": "Chapter 87 - Vehicles other than railway or tramway rolling-stock",
        "heading": "8708 - Parts and accessories of motor vehicles",
        "subheading": "8708.99 - Other parts and accessories",
        "code": "8708.99",
        "description": "Parts and accessories of motor vehicles, other",
        "keywords": "vehicle parts auto parts car parts spare parts automobile véhicules voitures",
        "checks": [
            "The item is identifiable as a part or accessory of a motor vehicle.",
            "The item is not excluded by the legal notes to Section XVII.",
            "No more specific subheading is available from the provided reference.",
        ],
    },
    {
        "section": "Section XVI - Machinery and mechanical/electrical equipment",
        "chapter": "Chapter 85 - Electrical machinery and equipment; sound/TV equipment",
        "heading": "8517 - Telephones and communication apparatus",
        "subheading": "8517.13 - Smartphones",
        "code": "8517.13",
        "description": "Smartphones for wireless networks",
        "keywords": "smartphone phone mobile telephone téléphone wireless network",
        "checks": [
            "The item is a smartphone or mobile telephone.",
            "The item is designed for cellular or other wireless networks.",
        ],
    },
    {
        "section": "Section XX - Miscellaneous manufactured articles",
        "chapter": "Chapter 94 - Furniture; bedding; lamps; prefabricated buildings",
        "heading": "9403 - Other furniture and parts thereof",
        "subheading": "9403.60 - Wooden furniture",
        "code": "9403.60",
        "description": "Wooden furniture, other than seats and medical/surgical furniture",
        "keywords": "furniture wood wooden meubles bois table cabinet",
        "checks": [
            "The item is furniture.",
            "The main material is wood.",
            "The item is not a seat, mattress, lamp, or prefabricated building.",
        ],
    },
]



# Complete high-level HS structure (Sections I-XXI and Chapters 01-97).
# This lets the user start from global classification, then move to chapter,
# then to headings/subheadings from the loaded HS/SH reference data.
HS_SECTIONS = [
    "Section I - Live animals; animal products",
    "Section II - Vegetable products",
    "Section III - Animal, vegetable or microbial fats and oils",
    "Section IV - Prepared foodstuffs; beverages; tobacco",
    "Section V - Mineral products",
    "Section VI - Products of the chemical or allied industries",
    "Section VII - Plastics, rubber and articles thereof",
    "Section VIII - Raw hides, skins, leather, furskins and articles thereof",
    "Section IX - Wood, cork, straw and articles thereof",
    "Section X - Pulp, paper and printed matter",
    "Section XI - Textiles and textile articles",
    "Section XII - Footwear, headgear, umbrellas and similar articles",
    "Section XIII - Articles of stone, plaster, cement, ceramic, glass",
    "Section XIV - Pearls, precious stones/metals and articles thereof",
    "Section XV - Base metals and articles of base metal",
    "Section XVI - Machinery and mechanical/electrical equipment",
    "Section XVII - Vehicles, aircraft, vessels and transport equipment",
    "Section XVIII - Optical, photographic, medical instruments; clocks; musical instruments",
    "Section XIX - Arms and ammunition",
    "Section XX - Miscellaneous manufactured articles",
    "Section XXI - Works of art, collectors' pieces and antiques",
]

HS_CHAPTERS_BY_SECTION = {
    HS_SECTIONS[0]: [
        "Chapter 01 - Live animals", "Chapter 02 - Meat and edible meat offal", "Chapter 03 - Fish and crustaceans, molluscs and other aquatic invertebrates", "Chapter 04 - Dairy produce, birds' eggs, honey and edible products of animal origin", "Chapter 05 - Products of animal origin, not elsewhere specified",
    ],
    HS_SECTIONS[1]: [
        "Chapter 06 - Live trees and other plants", "Chapter 07 - Edible vegetables and certain roots and tubers", "Chapter 08 - Edible fruit and nuts", "Chapter 09 - Coffee, tea, mate and spices", "Chapter 10 - Cereals", "Chapter 11 - Milling products, malt, starches and wheat gluten", "Chapter 12 - Oil seeds, industrial or medicinal plants, straw and fodder", "Chapter 13 - Lac, gums, resins and other vegetable saps", "Chapter 14 - Vegetable plaiting materials",
    ],
    HS_SECTIONS[2]: ["Chapter 15 - Animal, vegetable or microbial fats and oils"],
    HS_SECTIONS[3]: [
        "Chapter 16 - Preparations of meat, fish or crustaceans", "Chapter 17 - Sugars and sugar confectionery", "Chapter 18 - Cocoa and cocoa preparations", "Chapter 19 - Preparations of cereals, flour, starch or milk", "Chapter 20 - Preparations of vegetables, fruit or nuts", "Chapter 21 - Miscellaneous edible preparations", "Chapter 22 - Beverages, spirits and vinegar", "Chapter 23 - Residues and waste from food industries; prepared animal fodder", "Chapter 24 - Tobacco and manufactured tobacco substitutes",
    ],
    HS_SECTIONS[4]: ["Chapter 25 - Salt, sulphur, earths and stone", "Chapter 26 - Ores, slag and ash", "Chapter 27 - Mineral fuels, mineral oils and products of their distillation"],
    HS_SECTIONS[5]: [
        "Chapter 28 - Inorganic chemicals", "Chapter 29 - Organic chemicals", "Chapter 30 - Pharmaceutical products", "Chapter 31 - Fertilisers", "Chapter 32 - Tanning or dyeing extracts, dyes, paints and varnishes", "Chapter 33 - Essential oils and resinoids; perfumery and cosmetics", "Chapter 34 - Soap, washing preparations, waxes", "Chapter 35 - Albuminoidal substances; modified starches; glues; enzymes", "Chapter 36 - Explosives; pyrotechnic products; matches", "Chapter 37 - Photographic or cinematographic goods", "Chapter 38 - Miscellaneous chemical products",
    ],
    HS_SECTIONS[6]: ["Chapter 39 - Plastics and articles thereof", "Chapter 40 - Rubber and articles thereof"],
    HS_SECTIONS[7]: ["Chapter 41 - Raw hides and skins and leather", "Chapter 42 - Articles of leather; travel goods; handbags", "Chapter 43 - Furskins and artificial fur"],
    HS_SECTIONS[8]: ["Chapter 44 - Wood and articles of wood", "Chapter 45 - Cork and articles of cork", "Chapter 46 - Manufactures of straw, esparto or plaiting materials"],
    HS_SECTIONS[9]: ["Chapter 47 - Pulp of wood or other fibrous cellulosic material", "Chapter 48 - Paper and paperboard", "Chapter 49 - Printed books, newspapers and other printed products"],
    HS_SECTIONS[10]: [
        "Chapter 50 - Silk", "Chapter 51 - Wool, fine/coarse animal hair", "Chapter 52 - Cotton", "Chapter 53 - Other vegetable textile fibres", "Chapter 54 - Man-made filaments", "Chapter 55 - Man-made staple fibres", "Chapter 56 - Wadding, felt, nonwovens, special yarns", "Chapter 57 - Carpets and other textile floor coverings", "Chapter 58 - Special woven fabrics; lace; embroidery", "Chapter 59 - Impregnated, coated or laminated textile fabrics", "Chapter 60 - Knitted or crocheted fabrics", "Chapter 61 - Articles of apparel and clothing accessories, knitted or crocheted", "Chapter 62 - Articles of apparel and clothing accessories, not knitted or crocheted", "Chapter 63 - Other made up textile articles; sets; worn clothing",
    ],
    HS_SECTIONS[11]: ["Chapter 64 - Footwear", "Chapter 65 - Headgear", "Chapter 66 - Umbrellas, walking-sticks and similar", "Chapter 67 - Prepared feathers, artificial flowers, human hair articles"],
    HS_SECTIONS[12]: ["Chapter 68 - Articles of stone, plaster, cement, asbestos or mica", "Chapter 69 - Ceramic products", "Chapter 70 - Glass and glassware"],
    HS_SECTIONS[13]: ["Chapter 71 - Pearls, precious stones/metals, jewellery and coins"],
    HS_SECTIONS[14]: ["Chapter 72 - Iron and steel", "Chapter 73 - Articles of iron or steel", "Chapter 74 - Copper and articles thereof", "Chapter 75 - Nickel and articles thereof", "Chapter 76 - Aluminium and articles thereof", "Chapter 78 - Lead and articles thereof", "Chapter 79 - Zinc and articles thereof", "Chapter 80 - Tin and articles thereof", "Chapter 81 - Other base metals; cermets", "Chapter 82 - Tools, implements, cutlery of base metal", "Chapter 83 - Miscellaneous articles of base metal"],
    HS_SECTIONS[15]: ["Chapter 84 - Nuclear reactors, boilers, machinery and mechanical appliances", "Chapter 85 - Electrical machinery and equipment; sound/TV equipment"],
    HS_SECTIONS[16]: ["Chapter 86 - Railway or tramway locomotives and rolling-stock", "Chapter 87 - Vehicles other than railway or tramway rolling-stock", "Chapter 88 - Aircraft, spacecraft and parts thereof", "Chapter 89 - Ships, boats and floating structures"],
    HS_SECTIONS[17]: ["Chapter 90 - Optical, photographic, measuring, medical instruments", "Chapter 91 - Clocks and watches", "Chapter 92 - Musical instruments"],
    HS_SECTIONS[18]: ["Chapter 93 - Arms and ammunition; parts and accessories"],
    HS_SECTIONS[19]: ["Chapter 94 - Furniture; bedding; lamps; prefabricated buildings", "Chapter 95 - Toys, games and sports requisites", "Chapter 96 - Miscellaneous manufactured articles"],
    HS_SECTIONS[20]: ["Chapter 97 - Works of art, collectors' pieces and antiques"],
}

CHAPTER_TO_SECTION = {}
CHAPTER_TO_LABEL = {}
for _section, _chapters in HS_CHAPTERS_BY_SECTION.items():
    for _chapter_label in _chapters:
        _m = re.search(r"Chapter\s+(\d{2})", _chapter_label)
        if _m:
            CHAPTER_TO_SECTION[_m.group(1)] = _section
            CHAPTER_TO_LABEL[_m.group(1)] = _chapter_label


def chapter_number_from_code_or_label(value: str) -> str:
    value = str(value or "")
    m = re.search(r"Chapter\s+(\d{2})", value)
    if m:
        return m.group(1)
    digits = re.sub(r"\D", "", value)
    return digits[:2] if len(digits) >= 2 else ""


def official_section_for_code(code: str) -> str:
    chap = chapter_number_from_code_or_label(code)
    return CHAPTER_TO_SECTION.get(chap, "Uploaded HS/SH reference")



CLASSIFY_TEXT = {
    "English": {
        "page_doc": "Document review",
        "page_hs": "Determine HS code",
        "hs_title": "Determine HS/SH code",
        "hs_intro": "Answer the classification prompts from general level to specific level. This is a decision-support workflow; final classification must be validated by a qualified customs professional.",
        "product_desc": "Describe the good/product",
        "product_placeholder": "Example: cotton T-shirts / mechanical spare parts / smartphone / wooden furniture",
        "suggest": "Suggest from description",
        "section": "1. Select HS section",
        "chapter": "2. Select chapter",
        "heading": "3. Select heading",
        "subheading": "4. Select subheading",
        "checklist": "5. Confirm classification checklist",
        "result": "Recommended HS/SH code",
        "confidence": "Confidence",
        "exact_code": "Exact HS/SH code",
        "meaning": "Reference meaning",
        "why": "Why this result",
        "warning": "This is not a legal customs ruling. Validate with a customs broker/customs authority before declaration.",
        "no_match": "No direct suggestion found in the built-in sample/reference. Upload a complete HS/SH CSV reference or choose the closest HS section manually.",
        "use_code": "Use this HS code in document review text",
    },
    "Français": {
        "page_doc": "Revue documentaire",
        "page_hs": "Déterminer le code HS/SH",
        "hs_title": "Déterminer le code HS/SH",
        "hs_intro": "Répondez aux questions de classification du niveau général au niveau spécifique. Ce workflow aide à la décision; la classification finale doit être validée par un professionnel qualifié en douane.",
        "product_desc": "Décrire la marchandise/le produit",
        "product_placeholder": "Exemple : T-shirts en coton / pièces mécaniques / smartphone / meuble en bois",
        "suggest": "Suggérer à partir de la description",
        "section": "1. Choisir la section HS",
        "chapter": "2. Choisir le chapitre",
        "heading": "3. Choisir la position",
        "subheading": "4. Choisir la sous-position",
        "checklist": "5. Confirmer la checklist de classification",
        "result": "Code HS/SH recommandé",
        "confidence": "Confiance",
        "exact_code": "Code HS/SH exact",
        "meaning": "Signification de référence",
        "why": "Pourquoi ce résultat",
        "warning": "Ceci n’est pas une décision douanière légale. Validez avec un déclarant en douane ou l’autorité douanière avant déclaration.",
        "no_match": "Aucune suggestion directe trouvée. Commencez par choisir manuellement la section HS la plus proche.",
        "use_code": "Utiliser ce code HS dans le texte de revue documentaire",
    },
    "العربية": {
        "page_doc": "مراجعة الوثائق",
        "page_hs": "تحديد رمز HS",
        "hs_title": "تحديد رمز HS/SH",
        "hs_intro": "أجب على أسئلة التصنيف من المستوى العام إلى المستوى الدقيق. هذه وظيفة مساعدة فقط، ويجب التحقق النهائي مع المسرح الجمركي أو الجمارك قبل التصريح.",
        "product_desc": "صف البضاعة / المنتج",
        "product_placeholder": "مثال: قمصان قطنية / قطع ميكانيكية / هاتف ذكي / أثاث خشبي",
        "suggest": "اقتراح من الوصف",
        "section": "1. اختيار قسم HS",
        "chapter": "2. اختيار الفصل",
        "heading": "3. اختيار البند",
        "subheading": "4. اختيار البند الفرعي",
        "checklist": "5. تأكيد قائمة التحقق للتصنيف",
        "result": "رمز HS/SH المقترح",
        "confidence": "نسبة الثقة",
        "exact_code": "رمز HS/SH الدقيق",
        "meaning": "المعنى حسب المرجع",
        "why": "سبب هذا الاقتراح",
        "warning": "هذا ليس قراراً جمركياً قانونياً. يجب التحقق مع المسرح الجمركي أو الجمارك قبل التصريح.",
        "no_match": "لم يتم العثور على اقتراح مباشر. ابدأ باختيار أقرب قسم HS يدوياً.",
        "use_code": "استخدام هذا الرمز في نص مراجعة الوثائق",
    },
}


def build_classification_tree(hs_reference: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Use built-in examples and enrich them with uploaded HS/SH rows.

    Uploaded reference rows are mapped into the official HS Section and Chapter based
    on the first two digits of the HS code. This avoids showing everything under a
    generic “Uploaded reference” bucket and gives a real Section → Chapter → Heading
    → Subheading navigation path.
    """
    rows = []
    known = set()
    for base in HS_CLASSIFICATION_TREE:
        row = dict(base)
        code = normalize_code(row.get("code", ""))
        row["section"] = official_section_for_code(code) or row.get("section", "")
        row["chapter"] = official_chapter_for_code(code) or row.get("chapter", "")
        rows.append(row)
        if code:
            known.add(code)

    for ref in hs_reference or []:
        code = normalize_code(ref.get("code", ""))
        if code and code not in known:
            digits = re.sub(r"\D", "", code)
            heading = digits[:4] if len(digits) >= 4 else code
            rows.append({
                "section": official_section_for_code(code),
                "chapter": official_chapter_for_code(code),
                "heading": f"{heading} - {ref.get('description', '')[:90]}",
                "subheading": f"{code} - {ref.get('description', '')}",
                "code": code,
                "description": ref.get("description", ""),
                "keywords": ref.get("keywords", ""),
                "checks": [
                    "The product description corresponds to the loaded HS/SH reference description or keywords.",
                    "The material, use/function, and product form match this heading/subheading.",
                    "No more specific subheading in the loaded reference is more appropriate.",
                ],
            })
            known.add(code)

    # Add broad fallback catalog rows for common goods when not already loaded.
    try:
        existing = {str(r.get("code", "")) for r in rows}
        for code, description, keywords in BROAD_HS_KEYWORD_CATALOG:
            if code not in existing:
                rows.append(hs_row_from_catalog(code, description, keywords))
                existing.add(code)
    except Exception:
        pass

    return rows



# Broad fallback HS/SH suggestion catalog for common product words.
# This is a practical demo/search layer; exact classification still requires official HS/national tariff data.
BROAD_HS_KEYWORD_CATALOG = [

    ("8413.30", "Fuel, lubricating or cooling medium pumps for internal combustion piston engines", "electronic pump electric pump pump pumps pompe pompes مضخة مضخات fuel cooling lubricating automotive"),
    ("8413.50", "Other reciprocating positive displacement pumps", "pump pumps pompe pompes مضخة reciprocating displacement industrial pump"),
    ("8413.60", "Other rotary positive displacement pumps", "rotary pump gear pump vane pump pompe rotative مضخة"),
    ("8413.70", "Other centrifugal pumps", "centrifugal pump water pump pompe centrifuge مضخة ماء"),
    ("8413.81", "Pumps for liquids, other", "liquid pump water pump electronic pump electric pump pompe eau مضخة سائل"),
    ("8413.91", "Parts of pumps for liquids", "pump part pump parts pièces pompe spare pump"),
    ("8501.10", "Electric motors of an output not exceeding 37.5 W", "electric motor moteur électrique محرك كهربائي small motor"),
    ("8501.31", "DC motors and generators, output not exceeding 750 W", "dc motor electric motor moteur électrique"),
    ("8537.10", "Boards, panels and consoles for electric control or distribution, voltage not exceeding 1,000 V", "control panel electrical panel tableau électrique لوحة تحكم"),
    ("9032.89", "Automatic regulating or controlling instruments and apparatus, other", "controller regulator control unit sensor electronic control"),
    ("9026.20", "Instruments for measuring or checking pressure", "pressure sensor gauge manometer capteur pression"),
    ("9026.10", "Instruments for measuring or checking flow or level of liquids", "flow meter level sensor débitmètre capteur niveau"),
    ("8424.89", "Mechanical appliances for projecting, dispersing or spraying liquids or powders, other", "sprayer spray pump nozzle pulvérisateur رشاش"),
    ("8421.29", "Filtering or purifying machinery and apparatus for liquids, other", "filter purifier filtration liquid water filter filtre"),
    ("8419.89", "Machinery, plant or laboratory equipment involving temperature change, other", "heater cooler heat exchanger temperature equipment"),
    ("8422.30", "Machinery for filling, closing, sealing, labelling bottles, cans, boxes or containers", "packaging machine filling sealing labeling machine"),
    ("8428.90", "Lifting, handling, loading or unloading machinery, other", "conveyor lift handling machine elevator"),
    ("8467.29", "Tools for working in the hand, with self-contained electric motor, other", "electric tool drill grinder screwdriver outil électrique"),
    ("8479.89", "Machines and mechanical appliances having individual functions, other", "machine equipment apparatus industrial machinery"),
    ("8543.70", "Electrical machines and apparatus having individual functions, other", "electronic device electrical apparatus machine electronic module"),

    ("0101.21", "Live horses, pure-bred breeding animals", "horse horses cheval chevaux حصان خيل live animal"),
    ("0201.30", "Fresh or chilled boneless bovine meat", "beef meat bovine viande boeuf لحم بقر"),
    ("0302.89", "Fresh or chilled fish, other", "fish poisson سمك seafood"),
    ("0406.90", "Cheese and curd, other", "cheese fromage جبن dairy"),
    ("0701.90", "Potatoes, fresh or chilled, other", "potato potatoes pomme de terre بطاطا"),
    ("0803.90", "Bananas, fresh or dried", "banana bananas banane موز"),
    ("0901.21", "Roasted coffee, not decaffeinated", "coffee café قهوة roasted"),
    ("1006.30", "Semi-milled or wholly milled rice", "rice riz أرز"),
    ("1509.20", "Extra virgin olive oil", "olive oil huile olive زيت زيتون"),
    ("1704.90", "Sugar confectionery, not containing cocoa", "candy sweets bonbon حلوى confectionery"),
    ("1806.32", "Chocolate and other cocoa preparations", "chocolate chocolat شوكولاتة cocoa"),
    ("1905.31", "Sweet biscuits", "biscuit biscuits cookies cookie بسكويت"),
    ("2009.89", "Fruit or vegetable juices, other", "juice jus عصير fruit drink"),
    ("2202.99", "Non-alcoholic beverages, other", "soft drink soda beverage boisson مشروب"),
    ("2501.00", "Salt", "salt sel ملح"),
    ("2710.19", "Petroleum oils and oils from bituminous minerals, other", "oil petroleum fuel diesel gasoline petrol carburant"),
    ("3004.90", "Medicaments, in measured doses, other", "medicine medicament médicament دواء pharma"),
    ("3303.00", "Perfumes and toilet waters", "perfume parfum عطر fragrance"),
    ("3304.99", "Beauty or make-up preparations, other", "cosmetics makeup cream lotion beauté تجميل"),
    ("3401.11", "Soap and organic surface-active products for toilet use", "soap savon صابون"),
    ("3808.94", "Disinfectants", "disinfectant sanitizer désinfectant مطهر"),
    ("3923.21", "Plastic sacks and bags", "plastic bag bags sac plastique أكياس"),
    ("3926.90", "Articles of plastics, other", "plastic article plastique بلاستيك"),
    ("4011.10", "New pneumatic tyres, of rubber, for motor cars", "tire tyre tyres tires pneu pneus إطار سيارة"),
    ("4202.21", "Handbags with outer surface of leather", "bag handbag sac حقيبة leather"),
    ("4412.99", "Plywood, veneered panels and similar laminated wood", "plywood wood panel bois خشب"),
    ("4819.10", "Cartons, boxes and cases of corrugated paper or paperboard", "carton box cardboard carton emballage كرتون"),
    ("4901.99", "Printed books, brochures and similar printed matter", "book books livre livres كتاب printed"),
    ("5208.52", "Printed cotton woven fabrics", "fabric cotton textile tissu coton قماش"),
    ("6109.10", "T-shirts, singlets and other vests, knitted or crocheted, of cotton", "tshirt t-shirt shirt tee cotton coton قميص"),
    ("6110.20", "Jerseys, pullovers, cardigans and similar articles, of cotton", "sweater pullover jersey cardigan sweat-shirt قطن"),
    ("6203.42", "Men's or boys' trousers, breeches and shorts, of cotton", "trousers pants pantalon بنطال cotton coton"),
    ("6204.62", "Women's or girls' trousers, breeches and shorts, of cotton", "women trousers pants pantalon femme cotton"),
    ("6205.20", "Men's or boys' shirts, of cotton", "shirt shirts chemise قميص cotton"),
    ("6302.60", "Toilet linen and kitchen linen, of terry towelling cotton", "towel towels serviette منشفة cotton"),
    ("6403.99", "Footwear with outer soles of rubber/plastics/leather, other", "shoes shoe footwear chaussure حذاء"),
    ("6505.00", "Hats and other headgear, knitted or crocheted", "hat cap bonnet casquette قبعة"),
    ("6911.10", "Tableware and kitchenware, of porcelain or china", "plate dish porcelain ceramic assiette صحن"),
    ("7013.37", "Drinking glasses, other than of glass-ceramics", "drinking glass glasses cup verre كاس كوب زجاج"),
    ("7113.19", "Articles of jewellery, of precious metal, other", "jewelry jewellery bijou bijoux مجوهرات"),
    ("7210.49", "Flat-rolled products of iron or steel, plated/coated with zinc, other", "steel sheet metal acier فولاذ"),
    ("7308.90", "Structures and parts of structures, of iron or steel", "steel structure metal construction iron acier"),
    ("7318.15", "Screws and bolts, of iron or steel", "screw bolt screws bolts vis boulon برغي"),
    ("7323.93", "Table, kitchen or household articles, of stainless steel", "stainless steel kitchenware pot pan casserole"),
    ("7615.10", "Table, kitchen or household articles, of aluminium", "aluminum aluminium kitchenware pan pot"),
    ("8205.59", "Hand tools, other", "tool tools outil outils hand tool"),
    ("8414.51", "Table, floor, wall, window, ceiling or roof fans", "fan ventilateur مروحة"),
    ("8415.10", "Air conditioning machines, window or wall types", "air conditioner ac climatiseur مكيف"),
    ("8418.10", "Combined refrigerator-freezers", "refrigerator fridge freezer réfrigérateur ثلاجة"),
    ("8421.21", "Machinery for filtering or purifying water", "water filter filtration purifier filtre eau"),
    ("8443.32", "Printers, copying machines and facsimile machines", "printer printers imprimante طابعة"),
    ("8471.30", "Portable automatic data processing machines", "laptop computer ordinateur portable حاسوب"),
    ("8471.60", "Input or output units", "keyboard mouse écran monitor clavier souris"),
    ("8471.70", "Storage units", "hard disk ssd storage drive disque"),
    ("8481.80", "Taps, cocks, valves and similar appliances", "valve tap faucet robinet صنبور"),
    ("8483.90", "Transmission shafts, gears and gearing; parts", "gear shaft mechanical spare parts engrenage mécanique"),
    ("8504.40", "Static converters", "charger adapter power supply chargeur adaptateur"),
    ("8507.60", "Lithium-ion accumulators", "battery lithium batterie بطارية"),
    ("8516.50", "Microwave ovens", "microwave oven micro onde ميكروويف"),
    ("8517.13", "Smartphones", "smartphone phone mobile telephone téléphone هاتف"),
    ("8518.21", "Single loudspeakers, mounted in enclosure", "speaker loudspeaker haut-parleur سماعة"),
    ("8528.72", "Reception apparatus for television, colour", "television tv téléviseur تلفاز"),
    ("8536.50", "Electrical switches", "switch electrical interrupteur مفتاح كهربائي"),
    ("8544.42", "Electric conductors with connectors", "cable wire connector câble fil سلك"),
    ("8703.23", "Motor cars and other motor vehicles principally designed for transport of persons", "car automobile vehicle voiture سيارة"),
    ("8708.99", "Parts and accessories of motor vehicles, other", "car parts auto parts spare parts pièces سيارة"),
    ("8712.00", "Bicycles and other cycles, not motorised", "bicycle bike cycle vélo دراجة"),
    ("9004.90", "Spectacles, goggles and similar eyewear", "glasses spectacles goggles lunettes نظارات eyewear"),
    ("9018.90", "Medical, surgical or veterinary instruments and appliances, other", "medical instrument device hospital médical"),
    ("9102.11", "Wrist-watches, electrically operated", "watch watches montre ساعة"),
    ("9401.79", "Seats with metal frames, other", "chair chairs seat chaise كرسي"),
    ("9403.30", "Wooden furniture of a kind used in offices", "desk office furniture bureau meuble مكتب"),
    ("9403.60", "Wooden furniture, other", "wooden furniture meuble bois أثاث خشبي"),
    ("9405.19", "Chandeliers and other electric ceiling/wall lighting fittings", "lamp light lighting luminaire lampe مصباح"),
    ("9503.00", "Tricycles, scooters, dolls, toys and models", "toy toys jouet لعبة"),
    ("9506.99", "Articles and equipment for sports, other", "sport equipment ball ballon fitness"),
    ("9608.10", "Ball point pens", "pen pens ballpoint stylo قلم"),
]

def hs_row_from_catalog(code, description, keywords):
    chapter = code[:2]
    return {
        "section": official_section_for_code(code) if "official_section_for_code" in globals() else "",
        "chapter": official_chapter_for_code(code) if "official_chapter_for_code" in globals() else chapter,
        "heading": f"{code[:4]} - {description[:90]}",
        "subheading": f"{code} - {description}",
        "code": code,
        "description": description,
        "keywords": keywords,
        "checks": [
            "The product name and commercial description match this HS/SH reference.",
            "The material, use/function, and product form support this classification.",
            "A more specific national tariff subheading was checked before declaration.",
        ],
    }



def normalize_product_query_for_hs(text_value: str) -> str:
    """Normalize common misspellings and product synonyms for HS search."""
    q = (text_value or "").lower()
    replacements = {
        "pomp": "pump",
        "pompe": "pump",
        "pompes": "pump",
        "مضخة": "pump",
        "مضخات": "pump",
        "electrical": "electric",
        "electronic pump": "electric pump liquid pump",
        "electric pump": "pump liquid pump",
        "water pomp": "water pump",
        "water pompe": "water pump",
        "car pump": "pump automotive",
        "fuel pump": "pump fuel",
        "ordinateur": "computer",
        "portable computer": "laptop",
        "cell phone": "smartphone",
        "mobile phone": "smartphone",
        "chaise": "chair",
        "lunettes": "glasses",
        "velo": "bicycle",
        "vélo": "bicycle",
        "stylo": "pen",
    }
    for old, new in replacements.items():
        q = q.replace(old, new)
    return q


def suggest_hs_options(product_text: str, tree: List[Dict[str, str]], limit: int = 8) -> List[Dict[str, str]]:
    """Suggest HS rows using broad keyword, synonym, token, and fuzzy-ish matching.

    This is meant to make the demo searchable for many everyday product names.
    It is still not a legal classifier and should be backed by a complete HS/SH CSV.
    """
    product_lower = normalize_product_query_for_hs(product_text).strip()
    product_tokens = tokenize_for_match(product_lower)
    if not product_lower:
        return []

    # Simple synonym expansion by product family.
    synonym_map = {
        "chair": ["seat", "chaise", "كرسي"],
        "seat": ["chair", "chaise", "كرسي"],
        "glasses": ["spectacles", "goggles", "lunettes", "نظارات", "eyewear"],
        "spectacles": ["glasses", "lunettes", "eyewear"],
        "bicycle": ["bike", "cycle", "vélo", "دراجة"],
        "bike": ["bicycle", "cycle", "vélo"],
        "pen": ["ballpoint", "stylo", "قلم"],
        "phone": ["smartphone", "mobile", "telephone", "téléphone", "هاتف"],
        "car": ["automobile", "vehicle", "voiture", "سيارة"],
        "laptop": ["computer", "ordinateur", "pc"],
        "shoes": ["shoe", "footwear", "chaussure", "حذاء"],
        "shirt": ["t-shirt", "tshirt", "chemise", "قميص"],
        "trousers": ["pants", "pantalon", "بنطال"],
        "bag": ["handbag", "sac", "حقيبة"],
        "watch": ["montre", "ساعة"],
        "toy": ["jouet", "لعبة"],
        "lamp": ["light", "lighting", "lampe", "مصباح"],
        "battery": ["batterie", "بطارية"],
        "printer": ["imprimante", "طابعة"],
        "tire": ["tyre", "pneu", "إطار"],
    }

    expanded_tokens = set(product_tokens)
    for token in list(product_tokens):
        expanded_tokens.update(synonym_map.get(token, []))

    scored = []
    for row in tree:
        code = str(row.get("code", ""))
        haystack = " ".join([row.get("description", ""), row.get("keywords", ""), row.get("subheading", ""), row.get("heading", "")])
        haystack_lower = haystack.lower()
        score = similarity_score(product_text, haystack)

        # Direct phrase match is strongest.
        if product_lower and product_lower in haystack_lower:
            score += 60

        # Token and synonym matching.
        for token in expanded_tokens:
            tok = str(token).lower().strip()
            if len(tok) < 2:
                continue
            if tok in haystack_lower:
                score += 14 if len(tok) >= 4 else 6
            else:
                # crude fuzzy containment: match singular/plural and word starts
                singular = tok[:-1] if tok.endswith("s") and len(tok) > 3 else tok
                if singular and singular in haystack_lower:
                    score += 8

        # Family boosts.
        if any(w in product_lower for w in ["chair", "chairs", "seat", "chaise", "كرسي"]) and code.startswith("9401"):
            score += 60
        if any(w in product_lower for w in ["glasses", "spectacles", "goggles", "lunettes", "نظارات"]) and code.startswith("9004"):
            score += 60
        if any(w in product_lower for w in ["drinking glass", "glass cup", "glassware", "verre", "كأس", "كوب"]) and code.startswith("7013"):
            score += 60
        if any(w in product_lower for w in ["bicycle", "bike", "cycle", "vélo", "دراجة"]) and code.startswith("8712"):
            score += 60
        if any(w in product_lower for w in ["pen", "pens", "ballpoint", "stylo", "قلم"]) and code.startswith("9608"):
            score += 60
        if any(w in product_lower for w in ["pump", "pumps", "liquid pump", "water pump", "fuel pump"]) and code.startswith("8413"):
            score += 75
        if any(w in product_lower for w in ["electric motor", "motor", "moteur"]) and code.startswith("8501"):
            score += 55
        if any(w in product_lower for w in ["control panel", "electrical panel"]) and code.startswith("8537"):
            score += 55
        if any(w in product_lower for w in ["sensor", "pressure", "flow meter", "level sensor"]) and (code.startswith("9026") or code.startswith("9032")):
            score += 45
        if any(w in product_lower for w in ["electronic device", "electrical apparatus", "electronic module"]) and code.startswith("8543"):
            score += 40
        if any(w in product_lower for w in ["car", "voiture", "automobile", "passenger vehicle", "سيارة"]) and code.startswith("8703"):
            score += 60
        if any(w in product_lower for w in ["car part", "spare part", "vehicle part", "pièce", "piece", "parts"]) and code.startswith("8708"):
            score += 60

        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [row for score, row in scored[:limit] if score >= 8]




def get_openai_api_key():
    """Read OpenAI API key from Streamlit secrets or environment."""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY", "")




def get_google_vision_api_key():
    """Read Google Cloud Vision API key from Streamlit secrets or environment.

    This is useful when service account key creation is blocked by organization policy.
    Restrict the key to Cloud Vision API in Google Cloud Console.
    """
    try:
        key = st.secrets.get("GOOGLE_VISION_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GOOGLE_VISION_API_KEY", "")


def identify_object_with_google_vision_api_key(file_bytes: bytes) -> Tuple[str, str]:
    """Use Google Cloud Vision REST API with an API key for label/object detection."""
    api_key = get_google_vision_api_key()
    if not api_key:
        return "", "Google Vision API key is not configured."

    try:
        import base64
        import requests
    except Exception:
        return "", "Google Vision API-key mode needs the requests package. Add 'requests' to requirements.txt and redeploy."

    try:
        image_b64 = base64.b64encode(file_bytes).decode("utf-8")
        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
        payload = {
            "requests": [
                {
                    "image": {"content": image_b64},
                    "features": [
                        {"type": "OBJECT_LOCALIZATION", "maxResults": 10},
                        {"type": "LABEL_DETECTION", "maxResults": 10},
                    ],
                }
            ]
        }
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        if response.status_code >= 400:
            err = data.get("error", {})
            msg = err.get("message", str(data))
            return "", f"Google Vision API-key request failed: {msg}"

        result = (data.get("responses") or [{}])[0]
        if "error" in result:
            return "", f"Google Vision returned an error: {result['error'].get('message', result['error'])}"

        labels = []
        for item in result.get("localizedObjectAnnotations", []) or []:
            name = item.get("name")
            score = float(item.get("score", 0.0) or 0.0)
            if name:
                labels.append((name, score, "object"))
        for item in result.get("labelAnnotations", []) or []:
            name = item.get("description")
            score = float(item.get("score", 0.0) or 0.0)
            if name:
                labels.append((name, score, "label"))

        if not labels:
            return "", "Google Cloud Vision returned no labels/object names."

        return google_vision_labels_to_candidate(labels)
    except Exception as exc:
        return "", f"Google Vision API-key mode failed: {exc}"


def google_vision_labels_to_candidate(labels) -> Tuple[str, str]:
    """Convert Google Vision labels into a concise HS-search product candidate."""
    generic = {
        "product", "font", "line", "material property", "rectangle", "pattern",
        "electric blue", "wood", "floor", "table", "desk", "technology",
        "gadget", "office supplies", "writing", "stationery"
    }
    preferred_keywords = [
        "pen", "ballpoint", "phone", "smartphone", "chair", "bicycle", "bike",
        "pump", "shoe", "bag", "watch", "laptop", "computer", "shirt", "glasses",
        "spectacles", "keyboard", "mouse", "bottle", "cup", "lamp", "motor"
    ]

    ranked = []
    for name, score, kind in labels:
        n = str(name).lower().strip()
        rank = float(score or 0.0)
        if kind == "object":
            rank += 0.25
        if any(k in n for k in preferred_keywords):
            rank += 0.60
        if n in generic:
            rank -= 0.50
        ranked.append((rank, str(name), float(score or 0.0), kind))

    ranked.sort(reverse=True, key=lambda x: x[0])
    if not ranked:
        return "", "No usable Google Vision labels."

    all_label_text = " ".join(x[1].lower() for x in ranked[:8])
    if "pen" in all_label_text or "ballpoint" in all_label_text or "writing implement" in all_label_text:
        candidate = "ball point pen"
    elif "mobile phone" in all_label_text or "smartphone" in all_label_text or "phone" in all_label_text:
        candidate = "smartphone"
    elif "chair" in all_label_text or "seat" in all_label_text:
        candidate = "chair"
    elif "bicycle" in all_label_text or "bike" in all_label_text:
        candidate = "bicycle"
    elif "pump" in all_label_text:
        candidate = "liquid pump"
    elif "glasses" in all_label_text or "spectacles" in all_label_text or "goggles" in all_label_text:
        candidate = "spectacles glasses"
    else:
        candidate = ranked[0][1]

    label_summary = ", ".join([f"{name} ({kind}, {score:.2f})" for _, name, score, kind in ranked[:5]])
    return candidate[:120], f"Google Cloud Vision product candidate: {candidate}. Labels: {label_summary}."


def get_google_credentials_info():
    """Read Google Cloud service account JSON from Streamlit secrets or env."""
    raw = ""
    try:
        raw = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
    except Exception:
        raw = ""
    if not raw:
        raw = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")

    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return None

    return None


def identify_object_with_google_vision(file_bytes: bytes) -> Tuple[str, str]:
    """Use Google Cloud Vision to identify the main product.

    Preferred for Streamlit Cloud:
    - GOOGLE_VISION_API_KEY secret, because it does not require service account key files.

    Also supported:
    - GOOGLE_APPLICATION_CREDENTIALS_JSON service-account JSON secret
    - Google Application Default Credentials for local/Google Cloud workloads
    """
    if get_google_vision_api_key():
        return identify_object_with_google_vision_api_key(file_bytes)

    try:
        from google.cloud import vision
        from google.oauth2 import service_account
    except Exception:
        return "", "Google Cloud Vision needs google-cloud-vision, or configure GOOGLE_VISION_API_KEY for REST API-key mode."

    try:
        credentials_info = get_google_credentials_info()
        if credentials_info:
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            client = vision.ImageAnnotatorClient(credentials=credentials)
        else:
            client = vision.ImageAnnotatorClient()

        image = vision.Image(content=file_bytes)
        labels_response = client.label_detection(image=image, max_results=10)
        object_response = client.object_localization(image=image)

        if labels_response.error.message:
            return "", f"Google Vision label detection error: {labels_response.error.message}"

        object_note = ""
        if object_response.error.message:
            object_note = f" Google Vision object detection warning: {object_response.error.message}"

        labels = []
        for item in object_response.localized_object_annotations:
            if item.name:
                labels.append((item.name, float(item.score or 0.0), "object"))
        for item in labels_response.label_annotations:
            if item.description:
                labels.append((item.description, float(item.score or 0.0), "label"))

        candidate, note = google_vision_labels_to_candidate(labels)
        if object_note and note:
            note += object_note
        return candidate, note
    except Exception as exc:
        return "", f"Google Cloud Vision failed: {exc}"


def identify_object_with_vision_ai(file_bytes: bytes, mime_type: str = "image/jpeg") -> Tuple[str, str]:
    """Use a vision-capable AI model to identify the main trade object in an image.

    Returns: (short_product_description, warning_or_note)
    """
    api_key = get_openai_api_key()
    if not api_key:
        return "", "AI vision is not configured. Add OPENAI_API_KEY in Streamlit secrets to identify products from photos."

    try:
        import base64
        from openai import OpenAI
    except Exception:
        return "", "AI vision needs the OpenAI Python package. Add 'openai' to requirements.txt and redeploy."

    try:
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/jpeg"
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"

        model = os.environ.get("OPENAI_VISION_MODEL", "")
        try:
            model = st.secrets.get("OPENAI_VISION_MODEL", model)
        except Exception:
            pass
        model = model or "gpt-4o-mini"

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Identify the main physical product/object in this image for customs HS classification. "
                                "Return only a concise commercial product description, not a sentence. "
                                "Examples: ball point pen, smartphone, wooden chair, centrifugal water pump, cotton T-shirt. "
                                "If the image is unclear or no product is visible, return: unclear image"
                            ),
                        },
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
        )
        result = (getattr(response, "output_text", "") or "").strip()
        result = result.replace("\n", " ").strip()
        if not result:
            return "", "AI vision returned no object description."
        if "unclear" in result.lower():
            return "", "AI vision could not identify a clear product/object in the photo."
        return result[:120], f"AI vision identified product candidate using model: {model}"
    except Exception as exc:
        return "", f"AI vision failed: {exc}"


def is_image_upload(uploaded_file) -> bool:
    try:
        name = (uploaded_file.name or "").lower()
        mime = uploaded_file.type or ""
    except Exception:
        return False
    return mime.startswith("image/") or name.endswith((".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"))


def extract_product_candidate_from_text(document_text: str) -> str:
    """Extract a likely product/object name from manifest, invoice, OCR, or manual text."""
    raw = (document_text or "").strip()
    if not raw:
        return ""

    lines = [re.sub(r"\s+", " ", l).strip() for l in raw.splitlines() if re.sub(r"\s+", " ", l).strip()]
    joined = " ".join(lines)

    label_patterns = [
        r"Description\s+marchandise[s]?\s+(.{3,160})",
        r"Description of goods\s+(.{3,160})",
        r"Goods description\s+(.{3,160})",
        r"Product description\s+(.{3,160})",
        r"Description\s*:\s*(.{3,160})",
        r"Désignation\s*:\s*(.{3,160})",
        r"Marchandise[s]?\s*:\s*(.{3,160})",
    ]
    for pat in label_patterns:
        m = re.search(pat, joined, flags=re.IGNORECASE)
        if m:
            candidate = m.group(1)
            candidate = re.split(r"\b(HS|Code|Colis|Poids|Volume|Valeur|Origine|Qty|Quantity|Total)\b", candidate, flags=re.IGNORECASE)[0]
            candidate = re.sub(r"[^A-Za-zÀ-ÿ0-9\u0600-\u06FF /:'’,-]", " ", candidate)
            candidate = re.sub(r"\s+", " ", candidate).strip(" -/,")
            if len(candidate) >= 3:
                return candidate[:120]

    for line in lines:
        if re.search(r"\b\d{4}\.\d{2}\b|\b\d{4}\b", line) and not re.search(r"^\d+[\s/.-]*$", line):
            cleaned = re.sub(r"\b\d{4}(?:\.\d{2})?\b", " ", line)
            cleaned = re.sub(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(EUR|USD|GBP|TND|MAD|AED)?\b", " ", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\b(cartons?|palettes?|kg|cbm|eur|usd|origin|france|tunisia|ue)\b", " ", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"[^A-Za-zÀ-ÿ0-9\u0600-\u06FF /:'’,-]", " ", cleaned)
            cleaned = re.sub(r"\s+", " ", cleaned).strip(" -/,")
            if len(cleaned) >= 3:
                return cleaned[:120]

    if len(raw.strip()) < 3:
        return ""

    normalized = normalize_product_query_for_hs(raw) if "normalize_product_query_for_hs" in globals() else raw.lower()
    best = ""
    best_hits = 0
    try:
        for code, desc, keywords in BROAD_HS_KEYWORD_CATALOG:
            hits = 0
            for kw in re.findall(r"[A-Za-zÀ-ÿ0-9\u0600-\u06FF]+", keywords.lower()):
                if len(kw) >= 3 and kw in normalized:
                    hits += 1
            if hits > best_hits:
                best_hits = hits
                best = desc
    except Exception:
        pass
    if best:
        return best

    for line in lines:
        if len(line) >= 3 and not re.match(r"^(invoice|manifest|date|total|page)\b", line, flags=re.IGNORECASE):
            return line[:120]
    return raw[:120]


def hs_suggestions_dataframe(product_text: str, hs_reference):
    """Return a dataframe of HS suggestions for a product/document text."""
    try:
        tree = build_classification_tree(hs_reference)
        suggestions = suggest_hs_options(product_text, tree, limit=8)
        rows = []
        for s in suggestions:
            rows.append({
                "HS/SH": s.get("code", ""),
                "Section": s.get("section", ""),
                "Chapter": s.get("chapter", ""),
                "Heading": s.get("heading", ""),
                "Description": s.get("description", ""),
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def render_hs_classifier(lang: str, hs_reference: List[Dict[str, str]]):
    ct = CLASSIFY_TEXT[lang]
    tree = build_classification_tree(hs_reference)
    st.markdown(f'<div class="trade-title">🌍 TradeMindAI</div>', unsafe_allow_html=True)
    st.header(ct["hs_title"])
    st.info(ct["hs_intro"])

    product_text = st.text_area(ct["product_desc"], height=120, placeholder=ct["product_placeholder"], key="hs_product_text")

    st.markdown("**Object/HS detection from description, document, or photo**")
    st.caption("Use typed description for normal HS search. Upload/photo first uses OCR text; if Google Cloud Vision or OPENAI_API_KEY is configured, AI vision can identify the product from a pure photo.")
    hs_detect_method = st.radio(
        "HS input source",
        ["Use description above", "Upload image/PDF/document", "Take a picture"],
        horizontal=True,
        key="hs_detect_method",
    )

    detected_text_for_hs = ""
    if hs_detect_method == "Upload image/PDF/document":
        hs_upload = st.file_uploader(
            "Upload document/image for HS detection",
            type=["txt", "pdf", "docx", "png", "jpg", "jpeg", "webp", "tif", "tiff"],
            key="hs_object_upload",
        )
        if hs_upload is not None:
            detected_text_for_hs, hs_warning = extract_text_from_upload(hs_upload)
            if hs_warning:
                st.info(hs_warning)
            if detected_text_for_hs:
                st.text_area("Extracted text used for HS detection", detected_text_for_hs, height=140, key="hs_upload_extracted_text")
            elif is_image_upload(hs_upload):
                google_candidate, google_note = identify_object_with_google_vision(hs_upload.getvalue())
                if google_note:
                    st.info(google_note)
                if google_candidate:
                    detected_text_for_hs = google_candidate
                    st.success(f"Google Vision product candidate: {google_candidate}")
                else:
                    vision_candidate, vision_note = identify_object_with_vision_ai(hs_upload.getvalue(), hs_upload.type or "image/jpeg")
                    if vision_note:
                        st.info(vision_note)
                    if vision_candidate:
                        detected_text_for_hs = vision_candidate
                        st.success(f"AI vision product candidate: {vision_candidate}")
                    else:
                        st.warning("No readable text was extracted and no vision API could identify the product. Type the object name above.")
            else:
                st.warning("No readable text was extracted. For scanned PDFs/images, use a clearer file or connect AI vision for image understanding.")
    elif hs_detect_method == "Take a picture":
        st.info("For product photos, Google Cloud Vision will be used when GOOGLE_APPLICATION_CREDENTIALS_JSON is configured. Without a vision API, type the object name in the description field.")
        hs_photo = st.camera_input("Take a picture of the product/document", key="hs_object_camera")
        if hs_photo is not None:
            photo_bytes = hs_photo.getvalue()
            detected_text_for_hs, hs_warning = extract_text_from_image(photo_bytes)
            if hs_warning:
                st.info(hs_warning)
            if detected_text_for_hs:
                st.text_area("Text detected from photo", detected_text_for_hs, height=140, key="hs_photo_extracted_text")
            else:
                google_candidate, google_note = identify_object_with_google_vision(photo_bytes)
                if google_note:
                    st.info(google_note)
                if google_candidate:
                    detected_text_for_hs = google_candidate
                    st.success(f"Google Vision product candidate: {google_candidate}")
                else:
                    vision_candidate, vision_note = identify_object_with_vision_ai(photo_bytes, hs_photo.type or "image/jpeg")
                    if vision_note:
                        st.info(vision_note)
                    if vision_candidate:
                        detected_text_for_hs = vision_candidate
                        st.success(f"AI vision product candidate: {vision_candidate}")
                    else:
                        st.warning("Photo captured, but no readable text or clear product object was detected. Type the object name above.")

    if st.button("🔎 Look for HS code", key="look_for_hs_code_btn"):
        # Clear old result first so upload/photo failure does not reuse a previous search.
        st.session_state.pop("hs_last_candidate", None)
        st.session_state.pop("hs_active_product_text", None)

        source_for_detection = product_text.strip()
        if hs_detect_method != "Use description above":
            if detected_text_for_hs.strip():
                source_for_detection = detected_text_for_hs.strip()
            else:
                source_for_detection = ""

        if source_for_detection:
            candidate = extract_product_candidate_from_text(source_for_detection)
            st.session_state["hs_last_candidate"] = candidate or source_for_detection
            st.session_state["hs_active_product_text"] = candidate or source_for_detection
        else:
            st.warning("No product description or readable document text was found. Please type the product name/description above. Pure product-photo recognition needs a vision AI model.")

    if st.session_state.get("hs_active_product_text"):
        product_text = st.session_state.get("hs_active_product_text", product_text)
        st.success(f"Product used for HS search: {product_text}")
    elif not product_text.strip():
        st.info("Type a product description first, or upload a document/image that contains readable text.")

    suggestions = suggest_hs_options(product_text, tree, limit=8) if product_text.strip() else []
    if product_text.strip():
        if suggestions:
            st.caption(ct["suggest"])
            st.dataframe(pd.DataFrame([{
                "HS/SH": r["code"],
                "Section": r["section"],
                "Chapter": r["chapter"],
                "Heading": r["heading"],
                "Description": r["description"],
            } for r in suggestions]), width="stretch")
            best = suggestions[0]
            st.success(f"Best suggestion applied below: {best['section']} → {best['chapter']} → {best['code']}")
        else:
            st.warning(ct["no_match"])

    if not product_text.strip():
        st.stop()

    # 1) Section: show all official HS sections, not only the few rows in the sample reference.
    sections = list(HS_SECTIONS)
    extra_sections = sorted({r["section"] for r in tree if r.get("section") not in sections})
    sections += extra_sections
    default_section = suggestions[0]["section"] if suggestions and suggestions[0].get("section") in sections else sections[0]
    section = st.selectbox(ct["section"], sections, index=sections.index(default_section), key=f"hs_section_{suggestions[0]['code'] if suggestions else 'manual'}")

    # 2) Chapter: show all chapters belonging to that official section.
    chapters = HS_CHAPTERS_BY_SECTION.get(section, [])
    if not chapters:
        chapters = sorted({r["chapter"] for r in tree if r.get("section") == section}) or ["Uploaded reference chapter"]
    suggested_chapter = suggestions[0]["chapter"] if suggestions and suggestions[0].get("section") == section else None
    default_chapter = suggested_chapter if suggested_chapter in chapters else chapters[0]
    chapter = st.selectbox(ct["chapter"], chapters, index=chapters.index(default_chapter), key=f"hs_chapter_{suggestions[0]['code'] if suggestions else section}")
    chapter_num = chapter_number_from_code_or_label(chapter)

    # 3) Heading: from loaded/built-in reference rows under the selected chapter.
    chapter_rows = [r for r in tree if chapter_number_from_code_or_label(r.get("chapter", "")) == chapter_num]
    if not chapter_rows:
        st.warning("No heading/subheading is loaded for the selected chapter. Check that the selected section/chapter matches the suggestion above, or upload a complete HS/SH CSV reference for this chapter.")
        manual_code = st.text_input("Manual HS/SH code if known", placeholder="Example: 6109.10")
        manual_desc = st.text_input("Manual reference meaning/description", placeholder="Example: T-shirts, singlets and other vests, of cotton")
        selected = {
            "section": section,
            "chapter": chapter,
            "heading": "Manual heading",
            "subheading": manual_code or "Manual HS/SH code",
            "code": manual_code or "Not determined",
            "description": manual_desc or "No loaded reference description for this chapter.",
            "keywords": "",
            "checks": [
                "The selected section and chapter match the nature/function of the product.",
                "The exact heading/subheading was checked against an official HS/national tariff reference.",
                "The material, use/function, and product form support the selected code.",
            ],
        }
    else:
        headings = sorted({r["heading"] for r in chapter_rows})
        suggested_heading = suggestions[0]["heading"] if suggestions and chapter_number_from_code_or_label(suggestions[0].get("chapter", "")) == chapter_num else None
        default_heading = suggested_heading if suggested_heading in headings else headings[0]
        heading = st.selectbox(ct["heading"], headings, index=headings.index(default_heading), key=f"hs_heading_{suggestions[0]['code'] if suggestions else chapter_num}")

        sub_rows = [r for r in chapter_rows if r["heading"] == heading]
        sub_labels = [r["subheading"] for r in sub_rows]
        suggested_sub = suggestions[0]["subheading"] if suggestions and suggestions[0].get("heading") == heading else None
        default_sub = suggested_sub if suggested_sub in sub_labels else sub_labels[0]
        subheading = st.selectbox(ct["subheading"], sub_labels, index=sub_labels.index(default_sub), key=f"hs_subheading_{suggestions[0]['code'] if suggestions else heading}")
        selected = next(r for r in sub_rows if r["subheading"] == subheading)

    st.subheader(ct["checklist"])
    confirmations = []
    for idx, check in enumerate(selected.get("checks", []), 1):
        confirmations.append(st.checkbox(check, key=f"hs_check_{selected['code']}_{idx}"))

    confirmed = sum(1 for x in confirmations if x)
    total = max(1, len(confirmations))
    product_score = similarity_score(product_text, selected.get("description", "") + " " + selected.get("keywords", "")) if product_text.strip() else 0
    loaded_exact = selected.get("code") and selected.get("code") != "Not determined" and "No loaded reference" not in selected.get("description", "")
    confidence = min(100, int(round((confirmed / total) * 60 + min(product_score, 30) + (10 if loaded_exact else 0))))

    st.header(ct["result"])
    col1, col2 = st.columns(2)
    col1.metric(ct["exact_code"], selected["code"])
    col2.metric(ct["confidence"], f"{confidence}%")
    st.write(f"**{ct['meaning']}:** {selected['description']}")
    st.write(f"**{ct['why']}:** {section} → {chapter} → {selected.get('heading', '')} → {selected.get('subheading', '')}")
    if not loaded_exact:
        st.warning("This chapter is available, but no exact subheading is loaded for it. Upload a complete HS/SH or national tariff CSV to obtain exact codes for all chapters.")
    st.warning(ct["warning"])

    report = f"""TradeMindAI HS/SH Classification Suggestion
Generated: {datetime.now(UTC).isoformat()}
Language: {lang}
Product description: {product_text or 'Not provided'}

Section: {section}
Chapter: {chapter}
Heading: {selected.get('heading', '')}
Subheading: {selected.get('subheading', '')}
Recommended HS/SH code: {selected['code']}
Reference meaning: {selected['description']}
Checklist confirmed: {confirmed}/{total}
Confidence: {confidence}%

Compliance note: This is decision-support only. Final classification must be validated by a qualified customs professional/customs authority.
"""
    st.download_button("Download HS classification report", report, file_name="trademind_hs_classification.txt")


# -----------------------------
# UI
# -----------------------------
with st.sidebar:
    lang = st.selectbox("Language / Langue / اللغة", ["English", "Français", "العربية"])
    t = UI[lang]
    ct = CLASSIFY_TEXT[lang]
    page = st.radio("Feature / Fonction / الوظيفة", [ct["page_doc"], ct["page_hs"]], horizontal=False)
    tesseract_path = get_tesseract_cmd()
    lt = LOCAL_TEXT[lang]
    st.caption(f"Analysis model: TradeMindAI Rules + HS/SH hierarchy v33")
    hs_reference_file = st.file_uploader(lt["hs_upload"], type=["csv"], help=lt["hs_help"])
    hs_reference = load_hs_reference(hs_reference_file)
    st.caption(f"{lt["hs_model"]}: {len(hs_reference)} rows loaded")
    if tesseract_path:
        st.caption(f"OCR engine: {tesseract_path}")
    else:
        st.caption(lt["ocr_engine_missing"])
    if get_google_vision_api_key():
        st.caption("Google Cloud Vision: enabled with API key")
    elif get_google_credentials_info():
        st.caption("Google Cloud Vision: enabled with service account")
    else:
        st.caption("Google Cloud Vision: not configured")
    if get_openai_api_key():
        st.caption("OpenAI vision fallback: enabled")
    else:
        st.caption("OpenAI vision fallback: not configured")
    st.header(t["settings"])
    shipment_type = st.selectbox(t["shipment_type"], lt["shipment_options"])
    origin = st.text_input(t["origin"], placeholder="Tunisia / France / China")
    destination = st.text_input(t["destination"], placeholder="Czech Republic / UAE / Tunisia")
    doc_type = st.multiselect(t["documents"], lt["doc_options"], default=[lt["doc_options"][0]])

if lang == "العربية":
    st.markdown("""
    <style>
    .main .block-container, .stMarkdown, .stText, h1, h2, h3, p, label {direction: rtl; text-align: right;}
    [data-testid="stSidebar"] * {direction: rtl; text-align: right;}
    .stRadio > label {direction: rtl; text-align: right;}
    </style>
    """, unsafe_allow_html=True)

if page == CLASSIFY_TEXT[lang]["page_hs"]:
    render_hs_classifier(lang, hs_reference)
    st.stop()

st.markdown('<div class="trade-title">🌍 TradeMindAI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="trade-subtitle">{t["subtitle"]}</div>', unsafe_allow_html=True)
st.warning(t["warning"])

st.markdown('<div class="trade-card">', unsafe_allow_html=True)
input_method = st.radio(
    t["input_method"],
    [t["input_upload"], t["input_camera"], t["input_paste"]],
    horizontal=True,
)

extracted_blocks = []
warnings = []

if input_method == t["input_upload"]:
    uploaded_files = st.file_uploader(t["upload"], type=["txt", "pdf", "docx", "png", "jpg", "jpeg", "webp", "tiff"], accept_multiple_files=True)
    for uploaded in uploaded_files or []:
        text_part, warning = extract_text_from_upload(uploaded)
        if text_part:
            extracted_blocks.append(f"\n--- {uploaded.name} ---\n{text_part}")
        if warning:
            warnings.append(f"{uploaded.name}: {warning}")
elif input_method == t["input_camera"]:
    camera_image = st.camera_input(t["camera"])
    if camera_image is not None:
        text_part, warning = extract_text_from_image(camera_image.getvalue())
        if text_part:
            extracted_blocks.append(f"\n--- Camera image ---\n{text_part}")
        if warning:
            warnings.append(f"Camera image: {warning}")
else:
    st.info(LOCAL_TEXT[lang]["paste_info"])

st.markdown('</div>', unsafe_allow_html=True)

if warnings:
    for w in warnings:
        st.info(w)

st.caption(t["ocr_note"])
default_text = "\n".join(extracted_blocks).strip()
text = st.text_area(t["paste"], value=default_text, height=320, placeholder=LOCAL_TEXT[lang]["placeholder"])

if st.button(t["review"], type="primary"):
    if not text.strip():
        st.error(t["need_text"])
    else:
        result = review_document(text, lang, hs_reference)
        col1, col2, col3 = st.columns(3)
        col1.metric(t["risk_level"], result["risk_level"])
        col2.metric(t["risk_score"], f"{result['risk_score']}/100")
        col3.metric(t["hs_detected"], len(result["hs_codes"]))

        st.header(t["detected_fields"])
        st.write(", ".join(FIELD_LABELS[lang].get(x, x) for x in result["present"]) if result["present"] else LOCAL_TEXT[lang]["none"])

        st.header(t["missing"])
        if result["missing"]:
            st.dataframe(pd.DataFrame({LOCAL_TEXT[lang]["missing_col"]: [FIELD_LABELS[lang].get(x, x) for x in result["missing"]]}), width="stretch")
        else:
            st.success(LOCAL_TEXT[lang]["no_missing"])

        st.header(t["flags"])
        if result["flags"]:
            st.dataframe(pd.DataFrame([{LOCAL_TEXT[lang]["risk_area_col"]: RISK_LABELS[lang].get(f["risk_key"], f["risk_key"]), LOCAL_TEXT[lang]["matched_terms_col"]: f["matched_terms"]} for f in result["flags"]]), width="stretch")
        else:
            st.success(LOCAL_TEXT[lang]["no_flags"])

        st.header(t["codes_amounts"])
        st.subheader(LOCAL_TEXT[lang]["hs_codes_label"])
        if result.get("hs_details"):
            st.dataframe(pd.DataFrame(result["hs_details"]), width="stretch")
        else:
            st.info(LOCAL_TEXT[lang]["none_detected"])

        st.subheader(LOCAL_TEXT[lang]["amounts"])
        if result.get("amount_details"):
            st.dataframe(pd.DataFrame(result["amount_details"]), width="stretch")
        else:
            st.info(LOCAL_TEXT[lang]["none_detected"])

        st.header(LOCAL_TEXT[lang]["object_match"])
        if result.get("object_matches"):
            st.dataframe(pd.DataFrame(result["object_matches"]), width="stretch")
        else:
            st.info(LOCAL_TEXT[lang]["no_objects"])

        st.header(t["questions"])
        if result["questions"]:
            for q in result["questions"]:
                st.write(f"- {q}")
        else:
            st.write(LOCAL_TEXT[lang]["no_questions"])

        st.header(t["next_steps"])
        for i, step in enumerate(LOCAL_TEXT[lang]["next_steps_list"], 1):
            st.write(f"{i}. {step}")

        present_report = chr(10).join('- ' + FIELD_LABELS[lang].get(x, x) for x in result['present']) or LOCAL_TEXT[lang]["none"]
        missing_report = chr(10).join('- ' + FIELD_LABELS[lang].get(x, x) for x in result['missing']) or LOCAL_TEXT[lang]["none"]
        flags_report = chr(10).join('- ' + RISK_LABELS[lang].get(f["risk_key"], f["risk_key"]) + ': ' + f["matched_terms"] for f in result['flags']) or LOCAL_TEXT[lang]["none"]
        hs_report = chr(10).join('- ' + str(row) for row in result.get('hs_details', [])) or LOCAL_TEXT[lang]["none_detected"]
        amounts_report = chr(10).join('- ' + str(row) for row in result.get('amount_details', [])) or LOCAL_TEXT[lang]["none_detected"]
        questions_report = chr(10).join('- ' + x for x in result['questions']) or LOCAL_TEXT[lang]["none"]
        objects_report = chr(10).join('- ' + str(row) for row in result.get("object_matches", [])) or LOCAL_TEXT[lang]["none_detected"]

        report = f"""
TradeMindAI Customs Review Report
Generated: {datetime.now(UTC).isoformat()}
Language: {lang}
Shipment type: {shipment_type}
Origin: {origin or 'Not provided'}
Destination: {destination or 'Not provided'}
Documents: {', '.join(doc_type)}

Risk level: {result['risk_level']}
Risk score: {result['risk_score']}/100

Present fields:
{present_report}

Missing / unclear fields:
{missing_report}

Risk flags:
{flags_report}

Detected HS/SH details:
{hs_report}

Commercial amount details:
{amounts_report}

Manifest object-name / description check:
{objects_report}

Questions:
{questions_report}

Compliance note:
This report is for decision support only. Final customs classification and declarations must be validated by a qualified professional.
"""
        st.download_button(t["download"], report, file_name="trademind_review_report.txt")
