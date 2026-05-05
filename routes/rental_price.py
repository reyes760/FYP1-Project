from flask import Flask, request, jsonify, Blueprint
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import sys
import traceback
from datetime import datetime

rental_price_bp = Blueprint('rental_price', __name__)

# Load assets verbatim
current_dir = Path(__file__).resolve().parent
# Ensure these paths point to where you saved your training artifacts
model_path = current_dir.parent / 'models/linear_regression_model_for_rental_price.joblib'
assets_path = current_dir.parent / 'models/preprocessor_assets_for_rental_price.joblib'

model = joblib.load(str(model_path))
assets = joblib.load(str(assets_path))

scaler_milleage = assets['scaler_milleage']
scaler_year_diff = assets['scaler_year_diff']
brand_map = assets['brand_map']
model_map = assets['model_map']
state_map = assets['state_map']
gear_map = assets['gear_map']
global_mean_daily_rate = assets['global_mean_daily_rate']

# Load LabelEncoders
le_gear_type = assets['le_gear_type']
le_brand = assets['le_brand']
le_model = assets['le_model']
le_state = assets['le_state']

if not isinstance(assets, dict):
    raise TypeError(f"Expected assets to be a dict, but got {type(assets)}. check your joblib file.")

@rental_price_bp.route('/api/rental_price', methods=['POST'])
@rental_price_bp.route('/api/rental_price', methods=['POST'])
def predict_rental():
    try:
        # 1. Grab the stringified JSON data
        data = request.get_json()
        
        # 2. Extract inputs (Keep categories as strings for encoding)
        milleage = float(data.get('milleage', 0))
        input_year = int(data.get('year', 2026))
        gear_type = data.get('gear_type', "")
        brand = data.get('brand', "")
        model_name = data.get('model', "")
        state = data.get('state', "")

        # 3. Calculate Year_Diff (Current Year - Car Year)
        year_diff = 2026 - input_year

        # Preprocess numerical features
        mileage_scaled = scaler_milleage.transform(np.array([[milleage]]))[0][0]
        year_diff_scaled = scaler_year_diff.transform(np.array([[year_diff]]))[0][0]
        
        # Handle Brand
        if brand in le_brand.classes_:
            label = le_brand.transform([brand])[0]
            brand_encoded = brand_map.get(label, global_mean_daily_rate)
        else:
            brand_encoded = global_mean_daily_rate

        # Handle Model
        if model_name in le_model.classes_:
            label = le_model.transform([model_name])[0]
            model_encoded = model_map.get(label, global_mean_daily_rate)
        else:
            model_encoded = global_mean_daily_rate

        # Handle State
        if state in le_state.classes_:
            label = le_state.transform([state])[0]
            state_encoded = state_map.get(label, global_mean_daily_rate)
        else:
            state_encoded = global_mean_daily_rate

        # Handle Gear Type
        if gear_type in le_gear_type.classes_:
            label = le_gear_type.transform([gear_type])[0]
            gear_type_encoded = gear_map.get(label, global_mean_daily_rate)
        else:
            gear_type_encoded = global_mean_daily_rate


        # Create a DataFrame for prediction
        input_data = pd.DataFrame([[mileage_scaled, year_diff_scaled, gear_type_encoded, brand_encoded, model_encoded, state_encoded]],
                                columns=['Milleage', 'Year_Diff', 'Gear_Type', 'Brand', 'Model', 'State'])

        print(input_data) 
        # Make prediction
        predicted_log_daily_rate = model.predict(input_data)[0]

        # Inverse transform if the target was log-transformed
        predicted_daily_rate = np.exp(predicted_log_daily_rate) - 1

        return jsonify({
            'success': True,
            'prediction': float(predicted_daily_rate),
            'currency': 'RM'
        })
    
    except Exception as e:
        import sys
        # 1. Capture the traceback details
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # 2. Visual Debugging for your terminal
        print("\n" + "🚨" * 20)
        print(f" CRASH ON LINE: {line_number}")
        print(f" ERROR: {exc_type.__name__}: {str(e)}")
        
        # 3. CRITICAL: Print the state of your variables at the time of crash
        # This tells you if 'brand' or 'gear_type' came in as the wrong type or None
        print(f" DATA RECEIVED: {data}")
        print("🚨" * 20 + "\n")
        
        # 4. Detailed log for your own review
        traceback.print_exc()

        return jsonify({
            'success': False, 
            'error': f"Prediction Error: {str(e)}",
            'debug_info': {
                'line': line_number,
                'type': exc_type.__name__
            }
        }), 500