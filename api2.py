from flask import Flask, jsonify
import pandas as pd
import requests
import pyodbc


app = Flask(__name__)

# Chemin vers votre fichier Excel
EXCEL_FILE_PATH = "G:\\laboratoire\\02 Suivi statistique\\2-Programmes d'échange\\Compilation PTP 2024+.xlsx"

def read_excel_data(sheet_name='All'):
    # Lire le fichier Excel dans un DataFrame pandas
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet_name)
    return df

@app.route('/api/data', methods=['GET'])
def get_data():
    # Récupérer les données du fichier Excel
    sheet_name = 'All'
    try:
        data = read_excel_data(sheet_name)
        # Convertir le DataFrame en JSON
        data_json = data.to_dict(orient='records')
        return jsonify(data_json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)