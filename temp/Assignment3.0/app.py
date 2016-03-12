from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import os
from xml_helper import xml_obj
from collections import OrderedDict
from werkzeug import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_TEMPLATES = os.path.join(APP_ROOT, 'templates')
AUTHOR = "suharli2"
APP_SVN = "{}{}/".format("https://subversion.ews.illinois.edu/svn/sp16-cs242/", AUTHOR)


xml_list = os.path.join(APP_STATIC, 'svn_list_new.xml')
xml_log = os.path.join(APP_STATIC, 'svn_log_new.xml')
xml = xml_obj(xml_list, xml_log)

UPLOAD_FOLDER = os.path.join(APP_ROOT, 'upload')
ALLOWED_EXTENSIONS = ['xml']

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    """
    A function to upload file into local directory
    Give status of upload after redirect stored in session
    :return:
    :rtype:
    """
    if request.method == 'POST':
        file_list = request.files['list']
        file_log = request.files['log']
        if file_list and allowed_file(file_list.filename) and file_log and allowed_file(file_log.filename):
            filename_list = secure_filename(file_list.filename)
            filename_log = secure_filename(file_log.filename)

            file_list.save(os.path.join(UPLOAD_FOLDER, filename_list))
            file_log.save(os.path.join(UPLOAD_FOLDER, filename_log))
            global xml_list
            xml_list = os.path.join(UPLOAD_FOLDER, filename_list)
            global xml_log
            xml_log = os.path.join(UPLOAD_FOLDER, filename_log)
            global xml
            xml = xml_obj(xml_list, xml_log)
            session["upload_status"] = True
        else:
            session["upload_status"] = False
    else:
        session["upload_status"] = False

    return redirect(url_for('home'))


@app.route('/upload')
def upload():
    """
    Serve upload.html page
    """
    return render_template('upload.html')


@app.route('/')
def home():
    """
    Serve homepage of SvnHub
    Will call xml object to get all projects with its info
    """
    dict = xml.get_projects()
    result = OrderedDict(sorted(dict.items(), key=lambda t: t[0]))

    if "upload_status" in session and session["upload_status"] is not None:
        message = session["upload_status"]
        session["upload_status"] = None
        global AUTHOR
        global APP_SVN
        for res in result:
            AUTHOR = result[res]["author"]
            break
        APP_SVN = "{}{}/".format("https://subversion.ews.illinois.edu/svn/sp16-cs242/", AUTHOR)
        return render_template('index.html', projects=result, msg=message)
    return render_template('index.html', projects=result, msg=None)


@app.route('/tree/<path:url>')
def directory(url):
    """
    A function to generate a page full of dirs and files located at path <url>
    :param url: The path
    :type url: String
    """
    files = OrderedDict(sorted(xml.get_files(url).items(), key=lambda t: t[0]))
    dirs = OrderedDict(sorted(xml.get_dirs(url).items(), key=lambda t: t[0]))
    log = {}
    url_split = url.split('/')
    return render_template('show.html', files=files, dirs=dirs, url=url_split, APP_SVN=APP_SVN, _url=url, log=log)


@app.route('/rev/<int:rev>')
def revision(rev):
    """
    A function to generate data based on specific version number
    :param rev: revision number
    :type rev: int
    """
    dict = xml.get_log_by_rev(rev)
    return render_template('revision.html', dict=dict, APP_SVN=APP_SVN)


@app.route('/hist/<path:url>')
def history(url):
    """
    A function to generate html to list all revisions of a specific file
    specified by the param url
    :param url: the path to file
    :type url: string
    """
    result = dict()
    set = xml.get_rev_history(url)
    for rev in set:
        result[rev] = xml.get_log_by_rev(rev)
    result = OrderedDict(sorted(result.items(), key=lambda t: t[0], reverse=True))
    return render_template('history.html', dict=result, url_=url)


@app.route('/all')
def all_rev():
    """
    Simply display all revision numbers made to the repository
    """
    result = OrderedDict(sorted(xml.get_all_rev().items(), key=lambda t: t[0]))
    return render_template('all_revision.html', dict=result)

if __name__ == '__main__':
    app.secret_key=os.urandom(12)
    app.run(debug=True)
