from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

DATA_FOLDER = "/app/data"


@app.route('/api/data/<issuer_code>', methods=['GET'])
def get_data(issuer_code):
    """Чита податоци од `.xls` фајловите за даден издавач."""
    try:
        files = [f for f in os.listdir(DATA_FOLDER) if f.startswith(issuer_code)]
        if not files:
            return jsonify({"error": "No data found"}), 404

        all_data = []
        for file in files:
            file_path = os.path.join(DATA_FOLDER, file)
            df = pd.read_excel(file_path)
            all_data.append(df)

        combined_df = pd.concat(all_data, ignore_index=True)
        return jsonify(combined_df.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
