from transformers import pipeline
import torch
import spacy
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import asyncio
import nltk
# Descargar recursos necesarios de NLTK
nltk.download('stopwords')
nltk.download('punkt')
# Configurar dispositivo (CPU o GPU si disponible)
device = 0 if torch.cuda.is_available() else -1

# -------------------------------
# 1. RESUMEN - Modelo ligero en español
# -------------------------------
def process_sentences(sentences, stop_words=set(stopwords.words('spanish'))):
    summarized_sentences = []
    for sent in sentences:
        words = word_tokenize(sent.string)
        filtered_words = [word for word in words if word not in stop_words and word.isalnum()]
        summarized_sentences.append(' '.join(filtered_words))
    return summarized_sentences


def resumir_texto(texto):
    # Usar un modelo más ligero para resumen
    blob = TextBlob(texto)
    sentences = blob.sentences

    if len(texto.split()) < 10:
        return texto  # Para textos cortos, devolver el original
    
    try:
        # Limitar la longitud de entrada para optimizar
        resultado = process_sentences(sentences)
        return resultado
    except Exception as e:
        return f"Error en resumen: {str(e)}"

# -------------------------------
# 2. TRADUCCIÓN - Modelo más eficiente
# -------------------------------
def traducir_es_en(texto):
    try:
        # Modelo más ligero para traducción
        translator = pipeline(
            "translation_es_to_en", 
            model="Helsinki-NLP/opus-mt-es-en",
            device=device
        )
        resultado = translator(texto, max_length=400)
        return resultado[0]['translation_text']
    except Exception as e:
        return f"Error en traducción: {str(e)}"

# -------------------------------
# 3. SENTIMIENTOS - Modelo más rápido
# -------------------------------
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="pysentimiento/robertuito-sentiment-analysis",
    device=device
)

def analizar_sentimiento(texto):
    try:
        resultado = sentiment_analyzer(texto)[0]
        # Convertir etiquetas en español
        sentimiento_map = {
            "POS": "POSITIVO",
            "NEG": "NEGATIVO", 
            "NEU": "NEUTRO"
        }
        return {
            "sentimiento": sentimiento_map.get(resultado["label"], "NEUTRO"),
            "confianza": round(resultado["score"], 2)
        }
    except Exception as e:
        return {"sentimiento": "NEUTRO", "confianza": 0.0}

# -------------------------------
# 4. PALABRAS CLAVE - Alternativa ligera
# -------------------------------
def extraer_keywords(texto, top_n=3):
    """Extracción de palabras clave simple y eficiente"""
    try:
        # Usar spaCy si está disponible
        nlp = spacy.load("es_core_news_sm")
        doc = nlp(texto.lower())
        keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token) > 3]
        if keywords:
            return list(set(keywords))
        else:
            # Fallback simple
            import re
            palabras = re.findall(r'\b[a-záéíóúñ]{4,}\b', texto.lower())
            stopwords = {'que', 'con', 'para', 'por', 'como', 'pero', 'mas'}
            return [p for p in palabras if p not in stopwords][:top_n]
    except:
        return []

async def procesar_historial(texto, fecha = None):
    loop = asyncio.get_event_loop()
    resumen = await loop.run_in_executor(None, resumir_texto, texto)
    traduccion = await loop.run_in_executor(None, traducir_es_en, texto)
    sentimiento = await loop.run_in_executor(None, analizar_sentimiento, texto)
    keywords = await loop.run_in_executor(None, extraer_keywords, texto)

    return {
        "original": texto,
        "resumen": resumen,
        "traduccion": traduccion,
        "sentimiento": sentimiento,
        "palabras_clave": keywords,
        "fecha": fecha
    }