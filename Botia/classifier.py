from tensorflow.keras.applications.resnet50 import ResNet50, decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
from animal_facts import animal_facts

# Cargamos el modelo una sola vez
modelo = ResNet50(weights='imagenet')

def clasificar_imagen(ruta_imagen):
    try:
        img = image.load_img(ruta_imagen, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = modelo.predict(x)
        decoded = decode_predictions(preds, top=3)[0]

        # Filtrar solo resultados que sean animales (opcional)
        for pred in decoded:
            nombre = pred[1]
            if nombre.lower() not in ["web_site", "book_jacket", "comic_book"]:
                return nombre.replace("_", " ").capitalize()
        
        return "Especie desconocida"
    
    except Exception as e:
        print(f"[⚠️] Error al clasificar imagen: {e}")
        return "Especie desconocida"
