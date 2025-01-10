import os
import pandas as pd
from flask import Blueprint, jsonify

class DataProcessorSingleton:
    """
    Singleton class to handle data processing for the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        return cls._instance

    def get_data_folder(self):
        """
        Get the path to the data folder.

        Returns:
            str: Path to the data folder.
        """
        return self.data_folder

    def process_files(self, issuer_code):
        """
        Process files matching the issuer code and extract relevant data.

        Args:
            issuer_code (str): The issuer code to filter files.

        Returns:
            list: A list of dictionaries containing processed data.
        """
        matching_files = [
            f for f in os.listdir(self.data_folder) if f.startswith(issuer_code) and f.endswith(".xls")
        ]

        if not matching_files:
            raise FileNotFoundError(f"No data available for issuer code {issuer_code}.")

        df_list = []
        for file_name in matching_files:
            file_path = os.path.join(self.data_folder, file_name)
            print(f"Processing file: {file_path}")

            try:
                dfs = pd.read_html(file_path)
                for df in dfs:
                    print(f"Columns in {file_name}: {df.columns}")
                    if 'Date' in df.columns and 'Last trade price' in df.columns:
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
            raise ValueError("No valid data found for the specified issuer code.")

        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df.to_dict(orient='records')

routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route('/', methods=['GET'])
def home():
    """
    Home route to confirm API status.

    Returns:
        str: Message confirming API is running.
    """
    return "Flask API is running!"

@routes_blueprint.route('/api/data/<issuer_code>', methods=['GET'])
def get_data(issuer_code):
    """
    API route to fetch data for a specific issuer.

    Args:
        issuer_code (str): The code of the issuer to fetch data for.

    Returns:
        JSON: The processed data or an error message.
    """
    try:
        processor = DataProcessorSingleton()
        data = processor.process_files(issuer_code)
        return jsonify(data)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

