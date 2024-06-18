
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import requests
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)


app.config.from_object(Config)
mysql = MySQL(app)

# API
berita_api_url = 'https://newsapi.org/v2/top-headlines?country=id&apiKey=db40166cc7d54bccabd484374d5c89b6'
autogempa_url = 'https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json'
api_url = 'https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json'

@app.route('/')
def home():
    # Fetch berita from API
    berita_api = []
    autogempaurl = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(berita_api_url)
        response.raise_for_status()
        data = response.json()
        berita_api = data.get('articles', [])

        response1 = requests.get(autogempa_url, headers=headers)
        response1.raise_for_status()
        data1 = response1.json()
        autogempaurl = data1.get('Infogempa', {}).get('gempa', {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from news API: {e}")
    
    # Fetch berita from database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, judul, konten, tanggal FROM berita ORDER BY tanggal DESC")
    berita_db = cur.fetchall()
    cur.close()

    print(autogempaurl)
    
    return render_template('index.html', berita_api=berita_api, berita_db=berita_db, autogempaurl=autogempaurl)

@app.route('/berita/<int:id>')
def detail_berita(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM berita WHERE id = %s", (id,))
    berita = cur.fetchone()
    cur.close()
    return render_template('detail_berita.html', berita=berita)

@app.route('/infogempa')
def infogempa():
    gempa_list = []
    terbaru = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        gempa_list = data.get('Infogempa', {}).get('gempa', [])

        response1 = requests.get(autogempa_url, headers=headers)
        response1.raise_for_status()
        data1 = response1.json()
        terbaru = data1.get('Infogempa', {}).get('gempa', {})
    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Error fetching data from BMKG API: {e}")

    print(terbaru)
    return render_template('infogempa.html', gempa_list=gempa_list, terbaru=terbaru)

@app.route('/add', methods=['GET', 'POST'])
def add_berita():
    if request.method == 'POST':
        judul = request.form['judul']
        konten = request.form['konten']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO berita (judul, konten) VALUES (%s, %s)", (judul, konten))
        mysql.connection.commit()
        cur.close()
        flash('Berita berhasil ditambahkan!', 'success')
        return redirect(url_for('home'))
    return render_template('add_berita.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_berita(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM berita WHERE id = %s", (id,))
    berita = cur.fetchone()
    cur.close()
    if request.method == 'POST':
        judul = request.form['judul']
        konten = request.form['konten']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE berita SET judul = %s, konten = %s WHERE id = %s", (judul, konten, id))
        mysql.connection.commit()
        cur.close()
        flash('Berita berhasil diperbarui!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_berita.html', berita=berita)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/delete/<int:id>', methods=['POST'])
def delete_berita(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM berita WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Berita berhasil dihapus!', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
