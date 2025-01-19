from flask import Flask, jsonify
from data_fetcher import DataDownloader

app = Flask(__name__)

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    try:
        downloader = DataDownloader()
        downloader.main()
        return jsonify({"message": "Податоците се успешно преземени!"}), 200
    except Exception as e:
        return jsonify({"error": f"Грешка: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
