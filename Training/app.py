import tensorflow as tf
import tensorflow_hub as hub
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import os
from flask import Flask, request, render_template
import cv2

# Load model first
model = tf.keras.models.load_model(
    filepath='rice.h5',
    custom_objects={'KerasLayer': hub.KerasLayer}
)

app = Flask(__name__,  static_folder='../static',template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/details')  # Fixed the trailing slash
def pred():
    return render_template('details.html')  # Removed leading slash

@app.route('/result', methods=['POST'])  # Only need POST method here
def predict():
    if request.method == "POST":
        try:
            f = request.files['image']
            basepath = os.path.dirname(__file__)
            
            # Create directory if it doesn't exist
            upload_dir = os.path.join(basepath, 'Data')
            os.makedirs(upload_dir, exist_ok=True)
            
            filepath = os.path.join(upload_dir, f.filename)
            f.save(filepath)
            
            # Image preprocessing
            a2 = cv2.imread(filepath)
            if a2 is None:
                raise ValueError("Invalid image file")
            
            a2 = cv2.cvtColor(a2, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            a2 = cv2.resize(a2, (224, 224))
            a2 = np.array(a2, dtype=np.float32)  # Specify dtype explicitly
            a2 = a2 / 255.0
            a2 = np.expand_dims(a2, axis=0)

            # Prediction
            pred = model.predict(a2)
            class_names = ['arborio', 'basmati', 'ipsala', 'jasmine', 'karacadag']
            prediction = class_names[np.argmax(pred)]

            return render_template('results.html', prediction_text=prediction)
        
        except Exception as e:
            return render_template('error.html', error_message=str(e))

if __name__ == "__main__":
    app.run(debug=True)