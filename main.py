from pikepdf import Pdf, PdfImage
from flask import Flask, request, send_file, redirect, url_for, render_template, flash, session
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
import os, traceback
from zipfile import ZipFile


site = Flask(__name__)
site.config["UPLOAD_DIR"] = "pdfs" # for uploaded pdfs
site.config["OUTPUT_DIR"] = "images" # for downloadable images


for dir in ["UPLOAD_DIR", "OUTPUT_DIR"]:
    if not os.path.exists(site.config[dir]):
            os.mkdir(site.config[dir])

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extractImages(filename):
  zippedImages = ZipFile('images/pdfImages.zip', 'w')
  pdfFile = Pdf.open(filename)
  n = 1
  for page in pdfFile.pages:
    imgs = list(page.images.keys())
    for im in imgs:
      rawimage = page.images[im] 
      pdfimage = PdfImage(rawimage)
      f = pdfimage.extract_to(fileprefix='images/image_' + str(n))
      zippedImages.write(f)
      os.remove(f) # Delete the image once it is added to the zip file
      n += 1

  zippedImages.close()
  os.remove(filename) # Delete the PDF file once we are done

@site.route('/')
def home():
  return render_template('index.html')

@site.route('/process', methods=["POST"])
def upload_and_process():

    if "file" not in request.files: # invalid request
        # session['_flashes'].clear()
        flash("Invalid request.", "Error")
        return render_template('index.html')

    file = request.files['file']
    if file.filename == '': # no file uploaded by user
        # session['_flashes'].clear()
        flash("No file seleted.", "Error")
        return render_template('index.html')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(site.config['UPLOAD_DIR'], filename))

        try:
            extractImages(os.path.join(site.config['UPLOAD_DIR'], filename))
        except Exception as e:
            print(e)
            traceback.print_exc()
            # session['_flashes'].clear()
            flash("An error occurred. Please ensure that your pdf is correctly formatted and try again.", "Error")
            return render_template('index.html')
        else:
            # @site.after_request
            # def delete(response):
                #os.remove('images/pdfImages.zip') # delete the zip file after it has been downloaded
                # return response

            return send_file('images/pdfImages.zip',
              mimetype = 'zip',
              download_name= 'pdfImages.zip',
              as_attachment = True)
            # return redirect(url_for('download_file'))

@site.route('/download_file', methods=['GET'])
def download_file():
    # Zip file Initialization
    ## zipfolder = ZipFile('pdfImages2.zip','w') # Compression type 

    # zip all the files which are inside in the folder
    ## for root,dirs, files in os.walk('images/'):
        ## for file in files:
            ## zipfolder.write('images/'+file)
    ## zipfolder.close()

    return send_file('images/pdfImages.zip',
            mimetype = 'zip',
            download_name= 'pdfImages.zip',
            as_attachment = True)

    # Delete the zip file if not needed
    # os.remove("pdfImages2.zip")
    # os.remove("images/pdfImages1.zip")
    
site.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
site.run(host='0.0.0.0', port=8080)