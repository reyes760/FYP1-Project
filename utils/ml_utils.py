import os
import joblib

# Go up one level from /utils/ to find /data/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data')

def get_car_prediction(year, mileage, brand_name):
    try:
        model = joblib.load(os.path.join(DATA_PATH, 'car_resale_model.pkl'))
        le = joblib.load(os.path.join(DATA_PATH, 'brand_encoder.pkl'))

        # Convert Brand to Number
        try:
            brand_encoded = le.transform([brand_name])[0]
        except:
            brand_encoded = 0 

        # Predict using [Year, Mileage, Brand]
        prediction = model.predict([[int(year), float(mileage), brand_encoded]])
        return round(float(prediction[0]), 2)
    except Exception as e:
        print(f"ML Error: {e}")
        return None