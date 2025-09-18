import spacy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from googletrans import Translator
import re
import asyncio

# Configurar el traductor profesional
translator = Translator()

# Configurar spaCy con TextRank
try:
    nlp = spacy.load("es_core_news_sm")
    # Añadir TextRank al pipeline correctamente
    if "textrank" not in nlp.pipe_names:
        nlp.add_pipe("textrank", last=True)
    print("INFO -> spaCy y TextRank configurados correctamente")
except Exception as e:
    print(f"ERROR cargando spaCy: {e}")
    nlp = None

async def traducir_texto(texto, intentos=3):
    """Traducción usando Google Translate API."""
    for intento in range(intentos):
        try:
            translation = await translator.translate(texto, src='es', dest='en')
            return translation.text
        except Exception as e:
            print(f"Intento {intento + 1} fallido: {str(e)}")
            await asyncio.sleep(1)  # Esperar antes de reintentar
    return "Error en traducción después de múltiples intentos"

async def procesar_historial(texto_original, fecha=None):
    """Procesa el texto del historial con NLP profesional."""
    try:
        # Limpiar y preprocesar texto
        texto_limpio = texto_original.strip()
        if not texto_limpio:
            return crear_respuesta_error("Texto vacío", texto_original, fecha)

        # 1. Traducción con Google Translate
        traduccion = await traducir_texto(texto_limpio)
        
        # 2. Resumen (usando sumy con Luhn)
        resumen = generar_resumen(texto_limpio)
        
        # 3. Sentimientos (análisis mejorado)
        sentimiento_label, confianza = analizar_sentimiento_mejorado(texto_limpio)
        
        # 4. Palabras clave
        palabras_clave = extraer_palabras_clave_mejorado(texto_limpio)
        
        return {
            "original": texto_original,
            "resumen": resumen,
            "sentimiento": f"{sentimiento_label} ({confianza})",
            "traduccion": traduccion,
            "palabras_clave": palabras_clave,
            "fecha": fecha
        }
        
    except Exception as e:
        print(f"ERROR en procesar_historial: {str(e)}")
        return crear_respuesta_error(str(e), texto_original, fecha)

def generar_resumen(texto):
    """Genera resumen para textos."""
    try:
        if len(texto.split()) < 5:
            return "Texto corto - no requiere resumen"
            
        parser = PlaintextParser.from_string(texto, Tokenizer("spanish"))
        summarizer = LuhnSummarizer()
        resumen_oraciones = summarizer(parser.document, 1)
        
        return " ".join(str(s) for s in resumen_oraciones) if resumen_oraciones else "No se pudo generar resumen"
            
    except Exception as e:
        return f"Error en resumen: {str(e)}"

def analizar_sentimiento_mejorado(texto):
    """Análisis de sentimiento mejorado con diccionario expandido."""
    texto_lower = texto.lower()
    
    # Diccionario profesional basado en recursos lingüísticos reales
    palabras_positivas = {
        'bien': 0.7, 'bueno': 0.6, 'excelente': 0.9, 'mejor': 0.8, 
        'feliz': 0.8, 'contento': 0.7, 'alegre': 0.8, 'genial': 0.9,
        'perfecto': 1.0, 'óptimo': 0.9, 'estable': 0.5, 'normal': 0.4,
        'recuperado': 0.8, 'mejoría': 0.7, 'avance': 0.6, 'sano': 0.7,
        'saludable': 0.6, 'fortalecido': 0.7, 'aliviado': 0.8, 'positivo': 0.6
    }
    
    palabras_negativas = {
        'mal': -0.7, 'enfermo': -0.8, 'dolor': -0.9, 'triste': -0.8,
        'preocupado': -0.6, 'ansioso': -0.7, 'molesto': -0.6, 'peor': -0.8,
        'terrible': -0.9, 'grave': -0.8, 'crítico': -0.9, 'cansado': -0.5,
        'fatiga': -0.6, 'mareado': -0.7, 'náuseas': -0.8, 'fiebre': -0.7,
        'decaimiento': -0.7, 'debilidad': -0.6, 'inflamación': -0.6, 'sangrado': -0.8,
        'negativo': -0.6, 'complicado': -0.7, 'dificultad': -0.6
    }
    
    puntuacion = 0
    palabras_encontradas = 0
    
    # Buscar palabras con coincidencias exactas
    for palabra, valor in palabras_positivas.items():
        if re.search(r'\b' + re.escape(palabra) + r'\b', texto_lower):
            puntuacion += valor
            palabras_encontradas += 1
    
    for palabra, valor in palabras_negativas.items():
        if re.search(r'\b' + re.escape(palabra) + r'\b', texto_lower):
            puntuacion += valor
            palabras_encontradas += 1
    
    if palabras_encontradas > 0:
        puntuacion_promedio = puntuacion / palabras_encontradas
        confianza = abs(puntuacion_promedio)
        
        if puntuacion_promedio > 0.1:
            return "POSITIVO", round(confianza, 2)
        elif puntuacion_promedio < -0.1:
            return "NEGATIVO", round(confianza, 2)
        else:
            return "NEUTRO", round(confianza, 2)
    else:
        return "NEUTRO", 0.0

def extraer_palabras_clave_mejorado(texto):
    """Extrae palabras clave usando métodos mejorados."""
    try:
        if nlp is not None:
            # Usar TextRank para extracción profesional de palabras clave
            doc = nlp(texto)
            keywords = []
            
            for phrase in doc._.phrases[:5]:  # Top 5 frases clave
                keywords.append(phrase.text)
            
            if keywords:
                return keywords
    except Exception as e:
        print(f"Error en TextRank: {e}")
        # Fallback al método simple
    
    # Método simple como fallback
    stopwords = {'y', 'de', 'que', 'el', 'la', 'los', 'las', 'un', 'una', 
                'me', 'te', 'se', 'nos', 'os', 'mi', 'tu', 'su', 'mis', 'tus'}
    
    palabras = re.findall(r'\b[a-záéíóúñ]+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stopwords and len(p) > 2]
    
    return list(set(palabras_filtradas))[:5]  # Máximo 5 palabras

def crear_respuesta_error(error, texto_original, fecha):
    """Crea una respuesta de error estándar."""
    return {
        "original": texto_original,
        "resumen": f"Error: {error}",
        "sentimiento": "ERROR (0.0)",
        "traduccion": "No disponible",
        "palabras_clave": [],
        "fecha": fecha
    }

# Función de prueba
async def test_traduccion():
    """Prueba la traducción con ejemplos médicos."""
    textos_prueba = [
        "Me siento mal",
        "Tengo fiebre y dolor de cabeza",
        "El paciente presenta mejoría significativa",
        "Síntomas de gripe con temperatura elevada",
        "Dolor abdominal intenso con náuseas"
    ]
    
    for texto in textos_prueba:
        traduccion = await traducir_texto(texto)
        print(f"ES: {texto}")
        print(f"EN: {traduccion}")
        print("---")

