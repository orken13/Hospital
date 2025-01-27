from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

# Flask uygulaması oluşturuluyor
app = Flask(__name__)

# Veritabanı ayarları (sqlite kullandık)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hastane.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Veritabanı nesnesi
db = SQLAlchemy(app)

# ---------------------------
# Veritabanı Modelleri
# ---------------------------
class Patient(db.Model):
    # Hasta bilgilerini tutacak tablo
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    complaint = db.Column(db.String(200), nullable=False)

    # Doktor-hasta ilişkisi için foreign key kullanabiliriz
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)

class Doctor(db.Model):
    # Doktor bilgilerini tutacak tablo
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)

    # Bir doktorun birden çok hastası olabilir
    patients = db.relationship('Patient', backref='doctor', lazy=True)

# Veritabanında tabloların oluşturulması (eğer yoksa)
with app.app_context():
    db.create_all()

# ---------------------------
# HTML Sayfaları (Render)
# ---------------------------
@app.route('/')
def home():
    # Anasayfa için basit bir yönlendirme, index.html'i döndürüyoruz
    return render_template('index.html')

# ---- Hastalarla İlgili Sayfalar ---- #
@app.route('/patients')
def list_patients():
    # Tüm hastaları veritabanından çekip HTML sayfasına gönderiyoruz
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    # Hasta ekleme formu, GET ile sayfayı göster, POST ile form verisini al
    if request.method == 'POST':
        name = request.form['name']        # Form'daki "name" inputu
        age = request.form['age']          # Form'daki "age" inputu
        complaint = request.form['complaint']  # Form'daki "complaint" inputu

        # Yeni hasta nesnesi oluşturup veritabanına kaydediyoruz
        new_patient = Patient(name=name, age=age, complaint=complaint)
        db.session.add(new_patient)
        db.session.commit()

        # Kayıt sonrası hastalar listesine yönlendir
        return redirect(url_for('list_patients'))
    else:
        # GET isteğinde form sayfasını göster
        return render_template('add_patient.html')

@app.route('/patients/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    # Belirli bir hastayı ID üzerinden bulup silmek için
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    # Silme sonrası hastalar listesine dön
    return redirect(url_for('list_patients'))

# ---- Doktorlarla İlgili Sayfalar ---- #
@app.route('/doctors')
def list_doctors():
    # Tüm doktorları veritabanından çekip HTML sayfasına gönderiyoruz
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    # Doktor ekleme formu, GET ile sayfa göster, POST ile form verisi al
    if request.method == 'POST':
        name = request.form['name']
        specialty = request.form['specialty']

        new_doctor = Doctor(name=name, specialty=specialty)
        db.session.add(new_doctor)
        db.session.commit()

        return redirect(url_for('list_doctors'))
    else:
        return render_template('add_doctor.html')


# ---------------------------
# API Uç Noktaları (JSON)
# ---------------------------
# Opsiyonel olarak JSON cevap döndürmek istersem,
# örnek olması amacıyla 2 basit endpoint ekliyoruz.

@app.route('/api/patients', methods=['GET'])
def api_get_patients():
    # JSON olarak hasta listesi dönen basit bir endpoint
    patients = Patient.query.all()
    result = []
    for p in patients:
        result.append({
            'id': p.id,
            'name': p.name,
            'age': p.age,
            'complaint': p.complaint
        })
    return jsonify(result), 200

@app.route('/api/doctors', methods=['GET'])
def api_get_doctors():
    # JSON olarak doktor listesi dönen basit bir endpoint
    doctors = Doctor.query.all()
    result = []
    for d in doctors:
        result.append({
            'id': d.id,
            'name': d.name,
            'specialty': d.specialty
        })
    return jsonify(result), 200



if __name__ == '__main__':
    # Debug mod açık, kod değişikliklerini takip etmek için
    app.run(debug=True)
