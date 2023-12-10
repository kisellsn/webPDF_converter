import json
import os
import textwrap
import time
from urllib import response

from flask_cors import CORS
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify, make_response
from werkzeug.utils import secure_filename

import PIL.Image
from pyhtml2pdf import converter

from fpdf import FPDF

import shutil

from PyPDF2 import PdfWriter, PdfReader

import pandas as pd


app = Flask(__name__)
CORS(app)
app.config['RESULT_FOLDER']='resulted_files'
app.config['UPLOAD_FOLDER']='uploaded_files'

ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'docx', 'doc', 'csv', 'xlsx'}

#PAGES

@app.route("/")
def index():
    clean_folder("resulted_files")
    clean_folder("uploaded_files")
    return render_template("index.html")

@app.route("/merge_pdf")
def merge_pdf():
    clean_folder("resulted_files")
    clean_folder("uploaded_files")
    return render_template("merge.html")

@app.route("/convert_to_pdf")
def convert_to_pdf():
    clean_folder("resulted_files")
    clean_folder("uploaded_files")
    return render_template("convert.html")

@app.route("/convert_web_to_pdf")
def convert_web_to_pdf():
    clean_folder("resulted_files")
    clean_folder("uploaded_files")
    return render_template("web_convert.html")

@app.route("/result_pdf/<filename>")
def result_pdf(filename):
    pdf_read = PdfReader(f"resulted_files/{filename}.pdf")
    pages_count = pdf_read.pages
    file_stats = os.stat(f"resulted_files/{filename}.pdf")
    return render_template('result_pdf.html',
                           filename=filename,
                           pages_count=len(pages_count),
                           filesize=round(file_stats.st_size / 1024 / 1024, 2))


@app.route("/result_pdfs/<zipName>")
def result_pdfs(zipName):
    files = read_folder("resulted_files")
    make_zip(zipName)
    zip_file_size = os.path.getsize(f'{zipName}.zip')
    return render_template("result_pdfs.html",
                           filename=zipName,
                           filesize=round(zip_file_size / 1024 / 1024, 2),
                           files=files)



#FUNCTIONS

def make_zip(zipName):
    shutil.make_archive(zipName, 'zip', app.config['RESULT_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_converter(file):
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    file_name = file.filename.split('.')[0].lower()

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_name}.{file_extension}')
    output_path = os.path.join(app.config['RESULT_FOLDER'], f'{file_name}.pdf')
    match file_extension:
        case 'png' | 'jpg' | 'jpeg':
            image = PIL.Image.open(file)
            im = image.convert('RGB')
            im.save(output_path)
        case 'docx' | 'doc':
            pass

        case 'csv':
            file.save(input_path)
            CSV = pd.read_csv(input_path)
            path_to_html = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_name}.html')
            CSV.to_html(path_to_html)
            converter.convert(f'file:///{os.path.abspath(path_to_html)}', output_path)
        case 'xlsx':
            file.save(input_path)
            wb = pd.read_excel(input_path)
            path_to_html = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_name}.html')
            wb.to_html(path_to_html)
            converter.convert(f'file:///{os.path.abspath(path_to_html)}', output_path)
        case 'txt':
            file.save(input_path)
            with open(input_path, "r") as f:
                file_content = f.read()

            a4_width_mm = 210
            pt_to_mm = 0.35
            fontsize_pt = 14
            fontsize_mm = fontsize_pt * pt_to_mm
            margin_bottom_mm = 10
            character_width_mm = 7 * pt_to_mm
            width_text = a4_width_mm / character_width_mm

            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(True, margin=margin_bottom_mm)
            pdf.add_page()
            pdf.set_font(family='Times', size=fontsize_pt)
            splitted = file_content.split('\n')

            for line in splitted:
                lines = textwrap.wrap(line, width_text)

                if len(lines) == 0:
                    pdf.ln()

                for wrap in lines:
                    pdf.cell(0, fontsize_mm, wrap, ln=1)
            pdf.output(output_path)

        case _:
            # default case
            pass


@app.route("/upload", methods = ['GET', 'POST'])
def uploader():
    if request.method == 'POST':

        files = request.files.getlist('files[]')
        print(files)
        for file in files:
            if file.filename == '':
                print("there is no file")
                return 'redirect(request.url)'
            if file and allowed_file(file.filename):
                file_converter(file)
                #filename = secure_filename(file.filename)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower()=='pdf':
                merger_obj.append(file)
        try:
            merger_obj.write(os.path.join(app.config['RESULT_FOLDER'], secure_filename("mergedPdf.pdf")))
            merger_obj.close()
            return make_response(jsonify({
                "message": "success"
            }), 200)
        except Exception:
            return make_response(jsonify({
                "message": "error"
            }), 400)


@app.route('/web_convert', methods=['GET', 'POST'])
def web_converter():
    if request.method == 'POST':
        data = request.get_json()
        link = data.get('link')

        try:
            converter.convert(link, os.path.join(app.config['RESULT_FOLDER'], 'convertedPage.pdf'))
            return make_response(jsonify({
                "message": "success"
            }), 200)
        except Exception:
            return make_response(jsonify({
                "message": "error"
            }), 400)

@app.route("/result_pdf/show_file/<filename>")
def show_file(filename):
    return send_file(f"resulted_files/{filename}.pdf", as_attachment=False)

@app.route("/download", methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        data = request.get_json()
        filename = data.get('filename')
        filetype= data.get('filetype')
        

        if filetype == ".zip":
            file_path = f"{filename}{filetype}"
        else: file_path = f"resulted_files/{filename}{filetype}"
        download_name = data.get('newfilename', filename)

        return send_file(file_path, as_attachment=True, download_name=f"{download_name}{filetype}")



def clean_folder(folder_path: str):
    for entry in os.scandir(folder_path):
        file_path = os.path.join(folder_path, entry.name)
        try:
            if entry.is_file() or entry.is_symlink():
                os.unlink(file_path)
            elif entry.is_dir():
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def read_folder(folder_path:str):
    files_info = []
    for entry in os.scandir(folder_path):
        file_path = os.path.join(folder_path, entry.name)
        try:
            pdf_read = PdfReader(file_path)
            pages_count = len(pdf_read.pages)
        except Exception as e:
            pages_count = "Error: " + str(e)

        file_stats = os.stat(file_path)
        file_size = round(file_stats.st_size / 1024 / 1024, 2)


        file_info = {
            "file_name":entry.name,
            "path": file_path,
            "pages_count": pages_count,
            "file_size": file_size
        }
        files_info.append(file_info)
    return files_info


if __name__ == '__main__':
    app.run()
