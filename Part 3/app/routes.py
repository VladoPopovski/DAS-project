import pandas as pd
import os
from flask import Blueprint, jsonify

routes_blueprint = Blueprint('routes', __name__)


DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
print("DATA_FOLDER:", DATA_FOLDER)
print("Does data folder exist?", os.path.exists(DATA_FOLDER))


@routes_blueprint.route('/', methods=['GET'])
def home():
    return "Flask API is running!"


@routes_blueprint.route('/api/data/<issuer_code>', methods=['GET'])
def get_data(issuer_code):
    try:

        matching_files = [f for f in os.listdir(DATA_FOLDER) if f.startswith(issuer_code) and f.endswith(".xls")]

        if not matching_files:
            return jsonify({"error": f"Податоците за компанијата {issuer_code} не се достапни."}), 404

        df_list = []


        for file_name in matching_files:
            file_path = os.path.join(DATA_FOLDER, file_name)
            print(f"Processing file: {file_path}")
            try:

                dfs = pd.read_html(file_path)
                for df in dfs:
                    print(f"Columns in {file_name}: {df.columns}")

                    # Check if required columns exist
                    if 'Date' in df.columns and 'Last trade price' in df.columns:
                        # Rename columns to expected names
                        df.rename(columns={'Date': 'date', 'Last trade price': 'price'}, inplace=True)
                        df['date'] = pd.to_datetime(df['date'], errors='coerce')
                        df['price'] = pd.to_numeric(df['price'], errors='coerce')
                        df.dropna(subset=['date', 'price'], inplace=True)
                        df_list.append(df)
                    else:
                        print(f"Skipping file {file_name} due to missing required columns.")
            except Exception as e:
                print(f"Skipping file {file_path} due to error: {e}")

        if not df_list:
            return jsonify({"error": "Нема валидни податоци за овој издавач."}), 400

        combined_df = pd.concat(df_list, ignore_index=True)

        data = combined_df.to_dict(orient='records')
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Настана грешка: {str(e)}"}), 500
