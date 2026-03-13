from transformers import pipeline

# Cargar modelo de análisis de sentimientos forzando uso de PyTorch
classifier = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    framework="pt",
)

def analizar_texto(texto):
    resultado = classifier(texto)
    # Lógica para convertir los labels a una escala numérica si lo necesitas
    return resultado