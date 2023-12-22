import json
import os
from datetime import datetime
from io import BytesIO
import requests
from flask_cors import CORS
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from backend.functions import *
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
CORS(app)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
#---------------------------------GOOGLE---------------------------------
from oauthlib.oauth2 import WebApplicationClient
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL", None)

#GOOGLE_CLIENT_ID = json.load(open('conf.json', 'r+'))['web']['client_id']
client = WebApplicationClient(GOOGLE_CLIENT_ID)
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/google-login")
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/google-login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(token_url, headers=headers, data=body, auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET))
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint =google_provider_cfg["userinfo_endpoint"]
    uri,headers,body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]

        user = User.query.filter_by(username=users_email).first()
        if user:
            if bcrypt.check_password_hash(user.password, unique_id):
                login_user(user)
                return redirect(url_for('profile'))
        else:
            hashed_password = bcrypt.generate_password_hash(unique_id)
            new_user = User(username=users_email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('profile'))
    return redirect(url_for('index'))

#---------------------------------FILES---------------------------------
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_size = db.Column(db.Float)


#---------------------------------USER---------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_request
def before_request():
    if current_user.is_authenticated:
        app.jinja_env.globals['user_authenticated'] = True
    else:
        app.jinja_env.globals['user_authenticated'] = False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    files = db.relationship('File', backref='user', lazy=True)

    def is_authenticated(self):
        return True if self.is_authenticated else False

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Sing Up')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Log In')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('profile'))
    return render_template('login.html', form=form)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#---------------------------------PAGES---------------------------------
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_files = File.query.filter_by(user=current_user).order_by(File.created_at.desc()).all()

    for file in user_files:
        file_path = os.path.join(RESULT_FOLDER, file.filename)
        with open(file_path, 'wb') as f:
            f.write(file.data)
    return render_template('profile.html', user_files=user_files)

@app.route("/")
def index():
    clean_folder(RESULT_FOLDER)
    clean_folder(UPLOAD_FOLDER)

    return render_template("index.html")

@app.route("/merge_pdf")
def merge_pdf():
    clean_folder(RESULT_FOLDER)
    clean_folder(UPLOAD_FOLDER)
    return render_template("merge.html")

@app.route("/split_pdf")
def split_pdf():
    clean_folder(RESULT_FOLDER)
    clean_folder(UPLOAD_FOLDER)
    return render_template("split.html")

@app.route("/convert_to_pdf")
def convert_to_pdf():
    clean_folder(RESULT_FOLDER)
    clean_folder(UPLOAD_FOLDER)
    return render_template("convert.html")

@app.route("/convert_web_to_pdf")
def convert_web_to_pdf():
    clean_folder(RESULT_FOLDER)
    clean_folder(UPLOAD_FOLDER)
    return render_template("web_convert.html")

@app.route("/result_pdf/<filename>")
def result_pdf(filename):
    file_path = os.path.join(RESULT_FOLDER, f"{filename}.pdf")
    pdf_read = PdfReader(file_path)
    pages_count = pdf_read.pages
    file_size = round(os.stat(file_path).st_size / 1024 / 1024, 2)
    if current_user.is_authenticated:
        with open(file_path, 'rb') as file:
            file_data = file.read()
        new_file = File(filename=f"{filename}.pdf", data=file_data, user=current_user, file_size = file_size)
        db.session.add(new_file)
        db.session.commit()
    return render_template('result_pdf.html',
                           filename=filename,
                           pages_count=len(pages_count),
                           filesize=file_size)

@app.route("/result_pdfs/<zipName>")
def result_pdfs(zipName):
    files = [file_info for file_info in read_folder(RESULT_FOLDER) if file_info["file_name"].split('.')[-1] == "pdf"]
    if current_user.is_authenticated:
        for file in files:
            new_file = File(filename=file["file_name"], data=file["file_data"], user=current_user, file_size = file["file_size"])
            db.session.add(new_file)
        db.session.commit()


    make_zip(zipName)
    zip_file_size = os.path.getsize(os.path.join(RESULT_FOLDER, f'{zipName}.zip'))
    return render_template("result_pdfs.html",
                           filename=zipName,
                           filesize=round(zip_file_size / 1024 / 1024, 2),
                           files=files)

#---------------------------------FUNCTIONS---------------------------------
@app.route("/upload", methods = ['GET', 'POST'])
def uploader():
    if request.method == 'POST':

        files = request.files.getlist('files[]')
        for file in files:
            if file.filename == '':
                print("there is no file")
                return 'redirect(request.url)'
            if file and allowed_file(file.filename):
                file_converter(file)
            else:
                pass
        return make_response(jsonify({
            "message": "success"
        }), 200)

@app.route("/merge", methods = ['GET', 'POST'])
def merger():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        merger_obj = PdfWriter()
        for file in files:
            if '.' in file.filename and file.filename.rsplit('.', 1)[-1].lower()=='pdf':
                merger_obj.append(file)
        try:
            merger_obj.write(os.path.join(RESULT_FOLDER, secure_filename("mergedPdf.pdf")))
            merger_obj.close()
            return make_response(jsonify({
                "message": "success"
            }), 200)
        except Exception:
            return make_response(jsonify({
                "message": "error"
            }), 400)

@app.route("/split", methods=['POST'])
def divider():
    if request.method == 'POST':
        try:
            files = request.files.getlist('files[]')
            for file in files:
                if '.' in file.filename and file.filename.rsplit('.', 1)[-1].lower() == 'pdf':
                    input_path = os.path.join(UPLOAD_FOLDER, f'{file.filename}')
                    file.save(input_path)
                    pdf = PdfReader(input_path)
                    for page in range(len(pdf.pages)):
                        pdf_writer = PdfWriter()
                        pdf_writer.add_page(pdf.pages[page])

                        output_filename =  os.path.join(RESULT_FOLDER, '{}_page_{}.pdf'.format(file.filename.rsplit('.', 1)[0], page + 1))

                        with open(output_filename, 'wb') as out:
                            pdf_writer.write(out)
            return make_response(jsonify({
                "message": "success"
            }), 200)
        except Exception as e:
            print(e)
            return make_response(jsonify({
                "message": "error"
            }), 500)

@app.route('/web_convert', methods=['GET', 'POST'])
def web_converter():
    if request.method == 'POST':
        data = request.get_json()
        link = data.get('link')

        try:
            converter.convert(link, os.path.join(RESULT_FOLDER, 'convertedPage.pdf'))
            return make_response(jsonify({
                "message": "success"
            }), 200)
        except Exception:
            return make_response(jsonify({
                "message": "error"
            }), 400)

@app.route("/result_pdf/show_file/<filename>")
@app.route("/result_pdfs/show_file/<filename>")
@app.route("/show_file/<filename>")
def show_file(filename):
    return send_file(os.path.join(RESULT_FOLDER, f"{filename}.pdf"), as_attachment=False)

@app.route("/download", methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        data = request.get_json()
        filename = data.get('filename')
        filetype= data.get('filetype')
        file_path = f"{RESULT_FOLDER}/{filename}{filetype}"
        download_name = data.get('newfilename', filename)

        return send_file(file_path, as_attachment=True, download_name=f"{download_name}{filetype}")

@app.route('/DBdownload', methods=['GET', 'POST'])
def download_from_db():
    if request.method == 'POST':
        data = request.get_json()
        file_id = data.get('file_id')
        filetype = data.get('filetype')
        download_name = data.get('newfilename', data.get('filename'))

        file = File.query.get(file_id)
        if file:
            return send_file(BytesIO(file.data), download_name=f"{download_name}{filetype}", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
