from flask import Flask, render_template, request, redirect, url_for
from pony.orm import Database, PrimaryKey, Required, Optional, db_session, select
from datetime import datetime

app = Flask(__name__)

db = Database()

# Konfiguracija baze podataka (SQLite)
db.bind(provider='sqlite', filename='requests.db', create_db=True)

# Model zahtjeva
class Request(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    description = Required(str)
    assigned = Optional(bool, default=False)
    status = Required(str, default="Otvoren")

# Stvaranje tablica u bazi podataka
db.generate_mapping(create_tables=True)

# Popunjavanje baze podataka sa primjerima
with db_session:
    if not Request.exists():
        Request(title="Neispravna Tipkovnica", description="Ne radi tipkovnica", assigned=False, status="Otvoren")
        Request(title="Rezervacija IP adrese", description="Rezervairajte IP adresu 175.87.98.2", assigned=True, status="U tijeku")
        Request(title="Zaključan račun", description="Otključajte račun", assigned=True, status="Otvoren")
        Request(title="Problem sa računalom", description="Ne pali se", assigned=False, status="U tijeku")
        Request(title="Novi korisnik", description="Otvaranje korisničkog računa", assigned=True, status="U tijeku")
        Request(title="Problem sa printanjem", description="Ne printa", assigned=True, status="U tijeku")
        Request(title="Monitor ne radi", description="Crni Ekran", assigned=False, status="Otvoren")
        Request(title="Narudžba računala", description="Želim novo računalo", assigned=True, status="U tijeku")
        Request(title="Smrzava se", description="Outlook se smrzava", assigned=True, status="Zatvoren")
        Request(title="Novi program", description="Treba instalirati", assigned=False, status="Otvoren")
        Request(title="Uključivanje utičnice", description="Otvoriti utičnicu na switchu", assigned=True, status="U tijeku")
        Request(title="Gasi se", description="Monitor se svako malo gasi", assigned=True, status="Otvoren")
        Request(title="Razbijeni ekran", description="LAptop pao i razbio se", assigned=False, status="U tijeku")
        Request(title="Postavljanje novog uređaja", description="Postaviti, instalirati, aktivirati", assigned=True, status="U tijeku")
        Request(title="Odlazak korisnika", description="Zatvoriti korisnički račun", assigned=True, status="U tijeku")
        Request(title="Narudžba softvera", description="naručiti licencu", assigned=False, status="Otvoren")
        Request(title="Pristup podacima", description="Postavljanje prava pristupa", assigned=True, status="U tijeku")
        Request(title="Zaključan račun", description="Otključajte račun", assigned=False, status="Zatvoren")

# Glavna stranica
@app.route('/')
def index():
    with db_session:
        status_filter = request.args.get('status')
        assigned_filter = request.args.get('assigned')

        requests = Request.select()
        if status_filter:
            requests = requests.filter(lambda r: r.status == status_filter)
        if assigned_filter:
            assigned_bool = assigned_filter.lower() == 'true'
            requests = requests.filter(lambda r: r.assigned == assigned_bool)

        return render_template('index.html', requests=requests, status_filter=status_filter, assigned_filter=assigned_filter)

# Stranica za otvaranje novog zahtjeva
@app.route('/new_request', methods=['GET', 'POST'])
def new_request():
    if request.method == 'POST':
        with db_session:
            title = request.form['title']
            description = request.form['description']
            assigned = request.form.get('assigned', False)
            Request(title=title, description=description, assigned=assigned)
        return redirect(url_for('index'))
    return render_template('new_request.html')

# Stranica za uređivanje postojećeg zahtjeva
@app.route('/modify_request/<int:request_id>', methods=['GET', 'POST'])
def modify_request(request_id):
    with db_session:
        request_obj = Request.get(id=request_id)
        if request.method == 'POST':
            request_obj.title = request.form['title']
            request_obj.description = request.form['description']
            request_obj.assigned = request.form.get('assigned', False)
            request_obj.status = request.form['status']
            return redirect(url_for('index'))
    return render_template('modify_request.html', request=request_obj)

# Ruta za prikaz izvještaja
@app.route('/report')
def report():
    with db_session:
        statuses = [r.status for r in Request.select()]
        status_counts = {status: statuses.count(status) for status in set(statuses)}
    return render_template('report.html', status_counts=status_counts)


# Pokretanje aplikacije
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("5000"))