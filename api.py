from flask import Flask, jsonify
import pyodbc

app = Flask(__name__)

# Connexion à la base de données
def get_db_connection():
    conn = pyodbc.connect(
             'DRIVER={SQL Server Native Client 10.0};' # Indique le pilote ODBC utilisé pour la connexion.
             'SERVER=DBSQLQCQCRF02;' # Spécifie le nom du serveur où se trouve la base de données.
             'APP=Microsoft Office' # Identifie l'application établissant la connexion.
             'DATABASE=Laboratoire;' # Nomme la base de données à laquelle se connecter.
             'Trusted_Connection=yes;' # Utilise l'authentification Windows pour établir la connexion à la base de données.
            )
    return conn
    

@app.route('/data')
def get_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT NAIS_SAMPLES.SAMPLE_DATE, NAIS_SAMPLES.USER_SAMPLEID, NAIS_RESULTS.TESTID, NAIS_RESULTS.PROPERTYID, NAIS_RESULTS.NUMBER_VALUE
        FROM NAIS_SAMPLES
        INNER JOIN NAIS_RESULTS ON NAIS_SAMPLES.SAMPLE_ID = NAIS_RESULTS.SAMPLE_ID
        WHERE NAIS_SAMPLES.USER_SAMPLEID LIKE '5069%' AND NAIS_RESULTS.NUMBER_VALUE IS NOT NULL;
    ''')
    rows = cursor.fetchall()
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in rows]
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)