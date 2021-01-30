from flask import Flask, render_template, request, session, flash
from models.transaction import Transaction
from models.store import Store
from common.database import Database
from datetime import datetime
from jinja2 import Environment
from models.user import User
from models.decorators import requires_login


env = Environment(extensions=['jinja2_time.TimeExtension'])

env.datetime_format = '%a, %d %b %Y %H:%M:%S'
template = env.from_string("{% now 'utc' %}")

template.render()

app = Flask(__name__)
app.secret_key = "joe"


@app.route('/', methods=['POST', 'GET'])
def home_plate():
    return render_template('home.html')


@app.route('/index')
@requires_login
def home_index():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def new_user():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form['email']
        password = request.form['password']
        if email and password is not "":
            User(email, password).save_to_mongo()
            session['email'] = email
        else:
            flash("email and password required", "danger")
            return render_template('register.html')
    return render_template('index.html')


@app.route('/log_in', methods=['POST', 'GET'])
def log_in():
    if request.method == 'GET':
        return render_template('log_in.html')
    else:
        email = request.form['email']
        password = request.form['password']
        if User.find_user(email):
            if User.password_valid(email, password):
                session['email'] = email
                return render_template('index.html')
            else:
                flash("incorrect user or password", "danger")
                return render_template('log_in.html')
        else:
            return render_template('log_in.html')


@app.route('/index/transaction_entry/<string:store_id>', methods=['POST', 'GET'])
@requires_login
def create_method(store_id):
    if request.method == 'GET':
        return render_template('transaction_entry.html')
    else:
        sales = request.form["sales"]
        if sales.isnumeric():
            sales = int(sales)
        else:
            flash("sales must be a number, no commas or $ signs", "danger")
            return render_template('transaction_entry.html')
        traffic = request.form["traffic"]
        pieces = request.form["pieces"]
        drive = request.form["drive"]
        tran_date = request.form["date"]
        if tran_date is not '':
            tran_date = datetime.strptime(tran_date,'%Y-%m-%d')
        else:
            flash("a date is always required", "danger")
            return render_template("transaction_entry.html")
        store_id = store_id
        if sales and traffic and pieces and drive is not '':
            Transaction(sales, traffic, pieces, drive,  store_id, tran_date).save_to_mongo()
        else:
            flash("enter correct data in all fields", "danger")
    return render_template('transaction_entry.html')


@app.route('/store_new', methods=['GET', 'POST'])
@requires_login
def new_store():
    if request.method == "GET":
        return render_template('store_new.html')
    else:
        location = request.form["store"]
        number = request.form["number"]

        Store(location, number).save_to_mongo()
        stores = Store.find_stores()
        result_list = sorted(stores, key=lambda stores: int(stores.number))
    return render_template('store_index.html', stores=result_list)


@app.route('/store_index', methods=['GET', 'POST'])
@requires_login
def store_index():
    stores = Store.find_stores()

    result_list = sorted(stores, key=lambda stores: int(stores.number))

    return render_template('store_index.html', stores=result_list)


@app.route('/daily_report', methods=['GET', 'POST'])
def daily_report():
    report = Transaction.find_trans()
    trans = sorted(report, key=lambda report: str(report.tran_date))
    return render_template('daily_report.html', trans=trans)


@app.route('/report_by_date/<string:tran_date>', methods=['GET', 'POST'])
def date_report(tran_date):
    report = Transaction.find_by_date(tran_date)
    trans = sorted(report, key=lambda report: str(report.tran_date))
    return render_template('report_by_date.html', trans=trans)


@app.route('/report_by_range/<string:tran_date>', methods=['GET', 'POST'])
def date_range(tran_date):
    report = Transaction.find_by_week(tran_date)
    trans2 = sorted(report, key=lambda report: str(report.tran_date))
    return render_template('report_by_date.html', trans=trans2)


@app.route('/report_selector', methods=['GET', 'POST'])
def report_selector():
    if request.method == 'POST':
        tran_date = request.form['date']
        trans = Transaction.find_by_date(tran_date)
        return render_template('report_by_date.html', trans=trans)
    else: return render_template('report_selector.html')


@app.route('/week_selector', methods=['GET', 'POST'])
def week_selector():
    if request.method == 'POST':
        datetime = request.form['date']
        report = Transaction.find_by_week(datetime)
        trans = sorted(report, key=lambda report: str(report.tran_date))
        return render_template('report_by_range.html', trans=trans)
    else: return render_template('week_selector.html')


@app.before_first_request
def initialize_database():
    Database.initialize()


if __name__ == "__main__":
    app.run(debug=True)
