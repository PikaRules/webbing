import glob
import os
import yaml
import shutil
import re
from jinja2 import Template

template = Template('hello {{name}}!')
rs = template.render(name='pitufo')

#print glob.glob('*')
#print os.listdir('.')
#os.getcwd()
#print os.sep

"""
for path, directories, files in os.walk('.'):
    if 'tests' not in os.path.normpath(os.path.normcase(path)):
        print '-----'
        print path
        print directories
        print files
"""

#loading config.yaml file
APP_SETTINGS = None
with open('config.yaml') as config_file:
    APP_SETTINGS = yaml.safe_load(config_file)

print APP_SETTINGS


def load_file(path_and_name):
    file_data = None
    with open(path_and_name, "r") as myfile:
        file_data = myfile.read()
    return file_data


def create_new_file(path_and_name, data):
    """
    creates a new file. If the file already exists it will be overrited
    """
    name = re.sub('(\t)+', '/t', path_and_name)
    name = re.sub('(\a)+', '/a', name)
    name = re.sub('(\b)+', '/b', name)
    name = re.sub('(\f)+', '/f', name)
    name = re.sub('(\n)+', '/n', name)
    name = re.sub('(\r)+', '/r', name)
    name = re.sub('(\v)+', '/v', name)
    name = os.path.normpath(name)
    with open(os.path.normpath(name), "wb") as fo:
        fo.write(data)

section_directories_and_files = []

#get info per directory
for path, directories, files in os.walk(APP_SETTINGS['source_path']):
    if 'dist' not in os.path.normpath(os.path.normcase(path)):
        print '-----'
        print path
        print directories
        print files

        destination_path = APP_SETTINGS['destination_path']
        page_prefix = APP_SETTINGS['page_prefix']

        #find html files inside this directory
        index_paths = glob.glob(os.path.normpath(os.path.normcase(path)) + os.sep + 'index.html')
        pages_paths = glob.glob(os.path.normpath(os.path.normcase(path)) + os.sep + page_prefix + '*.html')

        #clean and create the destination directory
        dist_path = os.path.normpath(os.path.normcase(APP_SETTINGS['destination_path']))
        shutil.rmtree(dist_path, True)
        if not os.path.exists(dist_path):
            os.makedirs(dist_path)

        #creates relative directory
        full_destination_directory = os.path.normpath(os.path.normcase(destination_path)) + os.sep + os.path.normpath(os.path.normcase(path))
        if not os.path.exists(full_destination_directory):
            os.makedirs(full_destination_directory)

        section_directories_and_files.append({
            'pages_paths': pages_paths,
            'index_paths': index_paths,
            'base_path': path,
            'directories': directories,
            'files': files
        })


for section in section_directories_and_files:
    pages_paths = section['pages_paths']
    base_path = section['base_path']
    #generate jinja files
    for page_path in pages_paths:
        page_path_normalized = os.path.normpath(os.path.normcase(page_path))
        file_data_string = load_file(page_path_normalized)

        #create an render jinja template
        template = Template(file_data_string)
        html_string = template.render(name='pitufo')

        #get name
        file_path_stripped = page_path_normalized.split(os.sep)
        file_name = file_path_stripped[len(file_path_stripped) - 1]
        formated_file_name = re.sub('^page_._', '', file_name)
        formated_file_name = re.sub('^page_', '', formated_file_name)

        full_destination_path = os.path.normpath(os.path.normcase(destination_path)) + os.sep
        full_destination_path += os.path.normpath(os.path.normcase(base_path)) + os.sep + formated_file_name
        print full_destination_path
        create_new_file(full_destination_path, html_string)
