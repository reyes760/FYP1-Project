from flask import Flask, request, jsonify, Blueprint
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import traceback
from datetime import datetime

price_prediction_bp = Blueprint('price_prediction', __name__)

# --- Load Model and Preprocessing Tools Once ---
current_dir = Path(__file__).resolve().parent
# Ensure these paths point to where you saved your training artifacts
MODEL_PATH = current_dir.parent / 'models/linear_regression_model.joblib'
PREPROCESSOR_PATH = current_dir.parent / 'models/preprocessors.joblib'

# Load artifacts globally to avoid overhead on every request
try:
    model = joblib.load(MODEL_PATH)
    # This dictionary should contain your fitted StandardScaler and mapping dicts
    pre = joblib.load(PREPROCESSOR_PATH)
except Exception as e:
    print(f"Error loading model artifacts: {e}")
    model = None

@price_prediction_bp.route('/api/predict_range', methods=['POST'])
def calculate_car_price_prediction():
    if model and pre is None:
        return jsonify({'success': False, 'error': 'Model not initialized'}), 500

    try:
        data = request.get_json()
        
        brand = data.get('brand')
        milleage_input = float(data.get('milleage'))
        model_year = int(data.get('year'))
        gear_type = data.get('gear_type')
        state = data.get('state')
        
        # Determine current year dynamically
        current_year = datetime.now().year

        predictions = []
        
        # 2. Loop for 5-year range prediction
        for year_offset in range(6):
            # Calculate dynamic features for each year
            curr_milleage = milleage_input + (year_offset * 15000)
            # year_diff is the "age" of the car
            curr_year_diff = (current_year + year_offset) - model_year
            
            # 3. Preprocessing: Standardization
            # Use the scalers saved from your training session
            milleage_scaled = pre['scaler_milleage'].transform([[curr_milleage]])[0][0]
            year_diff_scaled = pre['scaler_year_diff'].transform([[curr_year_diff]])[0][0]

            # 4. Preprocessing: Label/Target Encoding[cite: 1]
            # Map strings to the target means (Log scale) defined during training
            gear_encoded = pre['gear_map'].get(gear_type, pre['global_mean'])
            brand_encoded = pre['brand_map'].get(brand, pre['global_mean'])
            state_encoded = pre['state_map'].get(state, pre['global_mean'])

            # 5. Prediction (Model outputs Log Price)[cite: 1]
            X_input = pd.DataFrame(
                [[milleage_scaled, year_diff_scaled, gear_encoded, brand_encoded, state_encoded]],
                columns=['Milleage', 'Year_Diff', 'Gear_Type', 'Brand', 'State']
            )
            
            prediction_log = model.predict(X_input)[0]

            # 6. Inverse Log Transformation[cite: 1]
            predicted_price = np.exp(prediction_log) - 1
            
            predictions.append(max(0, round(float(predicted_price), 2)))

        return jsonify({
            'success': True,
            'predictions': predictions,
            'years': ['2026', '2027', '2028', '2029', '2030', '2031']
        })

    except Exception as e:
        # 1. Import sys at the top of your file if you haven't already: import sys
        import sys 
        
        # 2. Extract the exact line number
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        
        # 3. Print a highly visible debug message to your Python terminal
        print("\n" + "🔥" * 25)
        print(f" CRASH DETECTED ON LINE {line_number} ")
        print(f" ERROR TYPE: {exc_type.__name__}")
        print(f" DETAILS: {str(e)}")
        print("🔥" * 25 + "\n")
        
        # Print the full stack trace just in case
        traceback.print_exc()
        
        # 4. Send the line number back to the frontend too
        return jsonify({
            'success': False, 
            'error': str(e),
            'failed_at_line': line_number
        }), 500