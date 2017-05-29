import os
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

with open('salon_list.txt', 'r') as f:
    salons = [l.rstrip('\n') for l in f]

#fileCounter = 1
# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    fileCounter = 1
    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():

    facename = request.form['facename']
    salon = request.form['salon']

    if request.files['file'] and not(os.path.exists('uploads/' + salon)):
        os.system('mkdir uploads/' + salon)
        with open('salon_list.txt', 'a') as f:
            f.write(salon + '\n')

    if request.files['file'] and not(os.path.exists('uploads/'+ salon + '/' + facename)):
        os.system('mkdir uploads/' + salon + '/' + facename)
        
    
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        #filename = facename
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'] + salon + '/' + facename + '/', filename))
        
        #fileCounter += 1
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        
        #Start Docker container in the background                                  
        #if fileCounter == 10:
        #fileCounter = 1
        os.system("sudo docker start 01a4d103a8a2")
        
        img_path = app.config['UPLOAD_FOLDER'] + salon + '/' + facename 

        #Write images from uploads folder to training-images in docker container                                                                                        
        os.system("sudo docker cp " + app.config['UPLOAD_FOLDER'] + salon + "/." + " zealous_goodall://root/openface/training-images/")
        os.system("sudo docker exec zealous_goodall /bin/sh -c \"cd /root/openface; ./util/align-dlib.py ./training-images/ align outerEyesAndNose ./aligned-images/ --size 96; ./batch-represent/main.lua -outDir ./generated-embeddings/" + salon + "/ -data ./aligned-images/; ./demos/classifier.py train ./generated-embeddings/" + salon + "/ \"")

        os.system("sudo docker exec zealous_goodall /bin/sh -c \"cd /root/openface; rm -rf aligned-images training-images \"")
        os.system("sudo docker exec zealous_goodall /bin/sh -c \"cd /root/openface; mkdir training-images \"")
        os.system("sudo docker cp theFaceDataset/karan zealous_goodall://root/openface/training-images/") #Karan will have to be replaced with some dummy person
        os.system("sudo docker stop 01a4d103a8a2")
        return redirect(url_for('uploaded_file',
                                filename=filename))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    #return send_from_directory(app.config['UPLOAD_FOLDER'] + salon + '/',
    #                           filename)
    return render_template('success.html')
    
if __name__ == '__main__':
        app.run(
            host="0.0.0.0",
            port=int("7575"),
            debug=True
        )
