# logic/nlp_processing.py
import asyncio
import nltk
from textblob import TextBlob
import re
from textblob import download_corpora
download_corpora.download_all()  # Esto descarga todos los recursos necesarios



# Descargar recursos necesarios de NLTK
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('brown')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Si usas torch/transformers/spacy, importarlos dentro de la carga para evitar costosos imports en cada llamada.
import torch
device = 0 if torch.cuda.is_available() else -1


# Recursos NLTK (quiet para no spamear)
#nltk.download('stopwords', quiet=True)
#nltk.download('punkt', quiet=True)

# Globals que se inicializan en load_nlp_model()
_spacy_nlp = None
_translator = None
_sentiment_analyzer = None

# ----- funciones ligeras (siempre disponibles) -----
def process_sentences(sentences, stop_words=set(nltk.corpus.stopwords.words('spanish'))):
    summarized_sentences = []
    for sent in sentences:
        words = nltk.word_tokenize(sent.string)
        filtered_words = [word for word in words if word not in stop_words and word.isalnum()]
        summarized_sentences.append(' '.join(filtered_words))
    return summarized_sentences

def resumir_texto(texto):
    blob = TextBlob(texto)
    sentences = blob.sentences
    if len(texto.split()) < 10:
        return texto
    try:
        return process_sentences(sentences)
    except Exception as e:
        return f"Error en resumen: {str(e)}"

# ----- funciones que usan los globals (evitan crear pipelines cada llamada) -----
def traducir_es_en(texto):
    global _translator
    if _translator is None:
        # Fallback: devolver texto original con nota
        return f"[Traducción no disponible]: {texto}"
    resultado = _translator(texto, max_length=400)
    return resultado[0]['translation_text']

def analizar_sentimiento(texto):
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        return {"sentimiento": "NEUTRO", "confianza": 0.0}
    resultado = _sentiment_analyzer(texto)[0]
    sentimiento_map = {"POS": "POSITIVO", "NEG": "NEGATIVO", "NEU": "NEUTRO"}
    return {"sentimiento": sentimiento_map.get(resultado["label"], "NEUTRO"),
            "confianza": round(resultado["score"], 2)}

def extraer_keywords(texto, top_n=3):
    global _spacy_nlp
    try:
        if _spacy_nlp is not None:
            doc = _spacy_nlp(texto.lower())
            keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token) > 3]
            return list(dict.fromkeys(keywords))[:top_n]  # quitar duplicados manteniendo orden
        # fallback regex simple
        palabras = re.findall(r'\b[a-záéíóúñ]{4,}\b', texto.lower())
        stopw = {'que', 'con', 'para', 'por', 'como', 'pero', 'mas'}
        return [p for p in palabras if p not in stopw][:top_n]
    except Exception:
        return []

# ----- función que procesa todo (usa las anteriores) -----
async def procesar_historial(texto, fecha=None):
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

# ----- Carga asíncrona y warm-up (llamar desde main.py) -----
async def load_nlp_model():
    """Carga pesado: spaCy, translator y sentiment pipeline. Ejecutar solo una vez."""
    global _spacy_nlp, _translator, _sentiment_analyzer
    if _spacy_nlp is None or _translator is None or _sentiment_analyzer is None:
        # Importar dentro para que importar el módulo sea barato
        from transformers import pipeline
        import spacy

        # Cargar spaCy en thread para no bloquear event loop
        if _spacy_nlp is None:
            _spacy_nlp = await asyncio.to_thread(spacy.load, "es_core_news_sm")
        # Cargar translator y sentiment con to_thread para no bloquear
        if _translator is None:
            _translator = await asyncio.to_thread(pipeline, "translation_es_to_en", "Helsinki-NLP/opus-mt-es-en", device=device)
        if _sentiment_analyzer is None:
            _sentiment_analyzer = await asyncio.to_thread(pipeline, "sentiment-analysis", "pysentimiento/robertuito-sentiment-analysis", device=device)

        # Warm-up breve (no bloquear, ejecutado en thread)
        try:
            await asyncio.to_thread(lambda: (_translator("hola"), _sentiment_analyzer("hola"), _spacy_nlp("hola")))
        except Exception:
            pass

    return {"spaCy": bool(_spacy_nlp), "translator": bool(_translator), "sentiment": bool(_sentiment_analyzer)}

def get_nlp_model():
    """Devuelve un dict con referencias (o None si no cargó)."""
    return {"spacy": _spacy_nlp, "translator": _translator, "sentiment": _sentiment_analyzer}
