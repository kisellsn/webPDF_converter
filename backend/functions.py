import os

import textwrap
import PIL.Image
from pyhtml2pdf import converter

from fpdf import FPDF

import shutil

from PyPDF2 import PdfWriter, PdfReader, PdfFileWriter, PdfFileReader
import pandas as pd

#import msoffice2pdf

RESULT_FOLDER='backend/resulted_files'
UPLOAD_FOLDER='backend/uploaded_files'
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


        file_info = {
            "file_name":entry.name,
            "path": file_path,
            "pages_count": pages_count,
            "file_size": file_size,
            "name": '.'.join(entry.name.split('.')[:-1]).lower(),
            "file_data": file_data
        }
        files_info.append(file_info)
    return files_info


def file_converter(file):
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    file_name = file.filename.split('.')[0].lower()

    input_path = os.path.join(UPLOAD_FOLDER, f'{file_name}.{file_extension}')
    output_path = os.path.join(RESULT_FOLDER, f'{file_name}.pdf')
    match file_extension:
        case 'png' | 'jpg' | 'jpeg':
            image = PIL.Image.open(file)
            im = image.convert('RGB')
            im.save(output_path)
        case 'docx' | 'doc':

            file.save(input_path)
            #msoffice2pdf.convert(source=input_path, output_dir="resulted_files",  soft=1)

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
def make_zip(zipName):
    shutil.make_archive(os.path.join(RESULT_FOLDER, f'{zipName}'), 'zip', RESULT_FOLDER)