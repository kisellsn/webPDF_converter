import os

from jinja2 import Environment
from jinja2 import FileSystemLoader
import pdfkit
import textwrap
import PIL.Image
from pyhtml2pdf import converter

from fpdf import FPDF

import shutil

from PyPDF2 import PdfWriter, PdfReader, PdfFileWriter, PdfFileReader
import pandas as pd


from backend_func.cloudmersive_converter import *


ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'docx', 'doc', 'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        with open(file_path, 'rb') as file:
            file_data = file.read()
        try:
            pdf_read = PdfReader(file_path)
            pages_count = len(pdf_read.pages)
        except Exception as e:
            pages_count = "Error: " + str(e)

        file_stats = os.stat(file_path)
        file_size = round(file_stats.st_size / 1024 / 1024, 2)
        _, file_extension = os.path.splitext(entry.name)

        file_info = {
            "file_name":entry.name,
            "path": file_path,
            "pages_count": pages_count,
            "file_size": file_size,
            "name": '.'.join(entry.name.split('.')[:-1]).lower(),
            "file_data": file_data,
            "file_extension": file_extension
        }
        files_info.append(file_info)
    return files_info


def file_converter(file):
    file_extension = file.filename.rsplit('.', 1)[-1].lower()
    file_name = file.filename.rsplit('.', 1)[0].lower()

    input_path = os.path.join(UPLOAD_FOLDER, f'{file_name}.{file_extension}')
    output_path = os.path.join(RESULT_FOLDER, f'{file_name}.pdf')
    match file_extension:
        case 'png' | 'jpg' | 'jpeg':
            image = PIL.Image.open(file)
            im = image.convert('RGB')
            im.save(output_path)
        case 'docx' | 'doc':
            file.save(input_path)
            cloudmersive_convert(input_path, output_path)
        case 'csv':
            file.save(input_path)
            CSV = pd.read_csv(input_path)
            path_to_html = os.path.join(UPLOAD_FOLDER, f'{file_name}.html')
            CSV.to_html(path_to_html)
            converter.convert(f'file:///{os.path.abspath(path_to_html)}', output_path)
        case 'xlsx':
            file.save(input_path)
            wb = pd.read_excel(input_path)
            path_to_html = os.path.join(UPLOAD_FOLDER, f'{file_name}.html')
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
            pdf.add_font("NotoSansDisplay", style="", fname="static/fonts/NotoSansDisplay-VariableFont_wdth,wght.ttf", uni=True)

            pdf.set_auto_page_break(True, margin=margin_bottom_mm)
            pdf.add_page()
            pdf.set_font(family='NotoSansDisplay', size=fontsize_pt)
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
def make_zip(zipName):
    shutil.make_archive(os.path.join("backend_func/result_zip", f'{zipName}'), 'zip', RESULT_FOLDER)

def create_pdf(name, job, about, email, LinkedIn, github, projects):
    template_vars = {
        'name': name,
        'job': job,
        'about':about,
        "email":email,
        "LinkedIn":LinkedIn,
        "github":github,
        "projects":projects
    }
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('generate.html')
    html_out = template.render(template_vars)
    pdfkit.from_string(html_out, f'{RESULT_FOLDER}/generate.pdf', configuration=config)