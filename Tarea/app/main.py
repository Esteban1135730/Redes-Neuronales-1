import os
import io
import base64
from flask import Flask, render_template, request, send_file
import pandas as pd
from wordcloud import WordCloud
from app.sentiment import analizar_texto
from app.text_utils import limpiar_texto

app = Flask(__name__)

# Definimos la carpeta de subidas de forma absoluta
UPLOAD_FOLDER = '/app/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No se subió archivo", 400
        
        file = request.files['file']
        # Leer Excel usando openpyxl y aceptar distintos nombres de columna
        df = pd.read_excel(file, engine="openpyxl")
        
        posibles_nombres = [
            'comentario', 'Comentario', 'comentarios', 'Comentarios',
            'texto', 'Texto', 'review', 'Review', 'opinion', 'Opinion'
        ]
        comentario_col = None
        for nombre in posibles_nombres:
            if nombre in df.columns:
                comentario_col = nombre
                break
        
        if comentario_col is None:
            return (
                "No se encontró una columna de comentarios. "
                "Agrega una columna llamada por ejemplo 'comentario' o 'Comentario'. "
                f"Columnas detectadas: {', '.join(map(str, df.columns))}",
                400,
            )
        
        # Procesamiento existente
        df['clean_text'] = df[comentario_col].apply(limpiar_texto)
        df['sentimiento'] = df['clean_text'].apply(lambda x: analizar_texto(x)[0]['label'])
        
        # Mapeo de etiquetas
        mapeo = {
            '1 stars': 'Muy Negativo', '2 stars': 'Negativo', '3 stars': 'Neutral', 
            '4 stars': 'Positivo', '5 stars': 'Muy Positivo'
        }
        df['sentimiento_humano'] = df['sentimiento'].replace(mapeo)
        
        # Generar nube de palabras (Nueva funcionalidad)
        texto_completo = " ".join(df['clean_text'].astype(str))
        wc = WordCloud(width=800, height=400, background_color='white').generate(texto_completo)
        
        img = io.BytesIO()
        wc.to_image().save(img, format='PNG')
        img.seek(0)
        wordcloud_url = base64.b64encode(img.getvalue()).decode()
        
        # Guardar archivo Excel
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resultados.xlsx')
        df.to_excel(output_path, index=False)
        
        stats = df['sentimiento_humano'].value_counts().to_dict()
        return render_template('result.html', stats=stats, wordcloud=wordcloud_url)
    
    return render_template('index.html')

@app.route('/download')
def download_file():
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'resultados.xlsx')
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "El archivo no existe.", 404

if __name__ == "__main__":
    # Solo tienes que asegurarte de que esto sea exactamente así:
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)