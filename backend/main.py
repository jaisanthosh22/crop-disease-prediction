from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array, load_img
from tensorflow.keras.applications.imagenet_utils import preprocess_input
import numpy as np
import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and class data
try:
    model = load_model("trained_model.h5")
    print("Model loaded successfully.")
except Exception as e:
    print("Error loading model:", e)

try:
    class_data = pd.read_csv('class-data.csv')
    class_names = class_data['classnames'].tolist()
    pesticides = class_data['Pesticides'].tolist()
    shops = class_data['Shop Available'].tolist()
    print("Class data loaded successfully.")
except Exception as e:
    print("Error loading class data:", e)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Read and preprocess the image
        contents = await file.read()
        img = load_img(BytesIO(contents), target_size=(128, 128))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Model prediction
        predictions = model.predict(img_array)[0]
        predictions_clean = [float(value) if np.isfinite(value) else 0.0 for value in predictions]

        # Find the class with the highest confidence
        predicted_index = int(np.argmax(predictions_clean))
        confidence = predictions_clean[predicted_index]

        # Validate index and retrieve class name, pesticide, and shop
        if 0 <= predicted_index < len(class_names):
            predicted_class = class_names[predicted_index]
            recommended_pesticides = pesticides[predicted_index]
            recommended_shop = shops[predicted_index]
        else:
            predicted_class = "Unknown Class"
            recommended_pesticides = "N/A"
            recommended_shop = "N/A"

        # Log detailed prediction info for debugging
        print(f"Raw predictions: {predictions}")
        print(f"Cleaned predictions: {predictions_clean}")
        print(f"Predicted class index: {predicted_index}")
        print(f"Predicted class name: {predicted_class}")
        print(f"Prediction confidence: {confidence}")
        print(f"Pesticides: {recommended_pesticides}")
        print(f"Shop: {recommended_shop}")

        # Return prediction in JSON format
        response = {
            "Predicted Disease": predicted_class,
            "Confidence": confidence,
            "Pesticides": recommended_pesticides,
            "Shop": recommended_shop
        }
        return JSONResponse(content=response)

    except Exception as e:
        print("Error during prediction processing:", e)
        return JSONResponse(
            content={"error": "Internal server error during prediction."},
            status_code=500
        )
