import streamlit as st
from openai import OpenAI
import os
from PIL import Image
import fitz  # PyMuPDF
import pytesseract

# 🌍 Language selection
language_options = ["English", "Spanish", "French", "Mandarin Chinese","Punjabi", "Arabic"]
preferred_language = st.selectbox("🌐 Choose the language for your explanation:", language_options)

# Translations for UI
ui_texts = {
    "English": {
        "title": "Understand your official Canadian government letters",
        "subtitle": "Upload your government letter and choose your preferred language.  \nWe’ll explain what it means in simple terms, and tell you exactly what to do next.",
        "upload_label": "Upload your document",
        "submit_button": "Get explanation",
        "error_no_text": "We couldn't read any text from the file. Try again with a clearer or more legible document.",
        "error_type": "Unsupported file type."
    },
    "Spanish": {
        "title": "Entiende tus cartas oficiales del gobierno de Canadá",
        "subtitle": "Sube tu carta oficial y elige el idioma que prefieras.  \nTe explicamos lo que significa y qué hacer después, en palabras simples.",
        "upload_label": "Sube tu documento",
        "submit_button": "Obtener explicación",
        "error_no_text": "No pudimos leer ningún texto del archivo. Intenta nuevamente con un documento más claro o legible.",
        "error_type": "Tipo de archivo no soportado."
    },
    "French": {
        "title": "Comprenez vos lettres officielles du gouvernement canadien",
        "subtitle": "Téléversez votre lettre officielle et choisissez la langue de votre choix.  \nNous vous expliquerons son contenu en des termes simples et vous guiderons sur la marche à suivre.",
        "upload_label": "Téléverser votre document",
        "submit_button": "Obtenir une explication",
        "error_no_text": "Nous n'avons pas pu lire le texte du fichier. Veuillez réessayer avec un document plus lisible.",
        "error_type": "Type de fichier non pris en charge."
    },
    "Mandarin Chinese": {
        "title": "了解您收到的加拿大政府官方信件",
        "subtitle": "上传您的信件并选择首选语言。\n我们将用简单明了的方式解释内容，并告诉您下一步该怎么做。",
        "upload_label": "上传文件",
        "submit_button": "获取解释",
        "error_no_text": "我们无法读取文件中的任何文字。请尝试上传更清晰或更易读的文件。",
        "error_type": "不支持的文件类型。"
    },
    "Punjabi": {
        "title": "ਆਪਣੀਆਂ ਕੈਨੇਡੀਅਨ ਸਰਕਾਰੀ ਚਿੱਠੀਆਂ ਨੂੰ ਸਮਝੋ",
        "subtitle": "ਆਪਣੀ ਚਿੱਠੀ ਅਪਲੋਡ ਕਰੋ ਅਤੇ ਆਪਣੀ ਮਨਪਸੰਦ ਭਾਸ਼ਾ ਚੁਣੋ।\nਅਸੀਂ ਤੁਹਾਨੂੰ ਸਧਾਰਨ ਸ਼ਬਦਾਂ ਵਿੱਚ ਦੱਸਾਂਗੇ ਕਿ ਇਹ ਕੀ ਹੈ ਅਤੇ ਅੱਗੇ ਕੀ ਕਰਨਾ ਹੈ।",
        "upload_label": "ਆਪਣੀ ਫ਼ਾਈਲ ਅਪਲੋਡ ਕਰੋ",
        "submit_button": "ਵਿਆਖਿਆ ਲਵੋ",
        "error_no_text": "ਅਸੀਂ ਫ਼ਾਈਲ ਤੋਂ ਕੋਈ ਵੀ ਪਾਠ ਨਹੀਂ ਪੜ੍ਹ ਸਕੇ। ਕਿਰਪਾ ਕਰਕੇ ਹੋਰ ਸਾਫ਼ ਜਾਂ ਪੜ੍ਹਨਯੋਗ ਦਸਤਾਵੇਜ਼ ਨਾਲ ਮੁੜ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "error_type": "ਇਹ ਫ਼ਾਈਲ ਕਿਸਮ ਸਹਾਇਕ ਨਹੀਂ ਹੈ।"
    },
    "Arabic": {
        "title": "فهم الرسائل الرسمية من الحكومة الكندية",
        "subtitle": "قم بتحميل الرسالة واختر لغتك المفضلة.\nسنشرح لك معناها بخطوات بسيطة، وسنرشدك لما يجب فعله بعد ذلك.",
        "upload_label": "حمّل المستند الخاص بك",
        "submit_button": "احصل على الشرح",
        "error_no_text": "لم نتمكن من قراءة أي نص من الملف. حاول مرة أخرى باستخدام مستند أوضح.",
        "error_type": "نوع الملف غير مدعوم."
    }
}
text = ui_texts.get(preferred_language, ui_texts["English"])

# App title and description
st.title(text["title"])
st.write(text["subtitle"])

# OpenAI API setup
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# File uploader and button
uploaded_file = st.file_uploader(f"### {text['upload_label']}", type=("txt", "md", "pdf", "jpg", "png", "jpeg"))
# 💅 Custom button styling
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #2c2f33;
        color: white;
        border: none;
        padding: 0.5em 1.5em;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1rem;
        transition: background-color 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #6c6fcb;
        color: white;
    }

    div.stButton > button:focus, div.stButton > button:active {
        background-color: #2c2f33 !important;
        color: white !important;
        outline: none;
        box-shadow: none;
    }
    </style>
""", unsafe_allow_html=True)


# Botón de submit
submit = st.button(text["submit_button"])

# Process the file and generate explanation
if submit and uploaded_file:
    file_type = uploaded_file.type
    document = ""

    # Extract text from file
    if file_type in ["text/plain", "text/markdown"]:
        document = uploaded_file.read().decode()
    elif file_type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
            for page in pdf:
                document += page.get_text()
    elif "image" in file_type:
        image = Image.open(uploaded_file)
        document = pytesseract.image_to_string(image)
    else:
        st.warning(text["error_type"])

    if document.strip():
        prompt_final = f"""
        You are an immigration and government communication expert in Canada.

        You help newcomers and residents understand official letters from Canadian institutions (e.g. IRCC, CRA, SAAQ, RAMQ, etc.).

        Your task is to:
        1. Detect the original language of the letter.
        2. Read the document carefully, do a summary and explain it using clear, professional, and easy-to-understand language in {preferred_language}.
        3. If any actions are required, list them in concise, numbered steps.

        Important:
        - If the content is related to legal matters, clearly state that the explanation is for informational purposes only and does not constitute legal advice.
        - If the letter concerns immigration (e.g., visas, permits, decisions from IRCC), refer the user to AskAïa for a personalized consultation with certified experts: [Book your consultation](https://askaia.ca/en/book-your-immigration-consultation)

        Maintain a formal and respectful tone. Your response should be clear, concise, and accessible for people who may not be fluent in English or familiar with Canadian administrative systems.

        Here is the letter content:
        {document}
        """

        messages = [{"role": "user", "content": prompt_final}]
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        st.markdown("### Explanation")
        st.write_stream(stream)
    else:
        st.warning(text["error_no_text"])