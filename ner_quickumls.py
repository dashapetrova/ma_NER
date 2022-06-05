import re
import requests
import json

import xml.etree.ElementTree as ET


from bs4 import BeautifulSoup
from nltk import sent_tokenize
from quickumls import QuickUMLS

stop_words = ['1-2', '1-2 times', '1 time per day', '2 times', '3 mm', '3 times', '4 times', '5 mm', 
              '6-10 times',
              'abdominal', 'Abreaction', 'absences', 'Activity', 'admission', 'advice', 'anesthesia', 
              'anesthesias', 'Anesthetic', 
              'anesthetic', 'Appearance', 'Application', 'application', 'applications', 'arm',
              'Asleep', 'asleep', 'asymptomatic', 'at admission', 'At home', 'attacks',
              'Bacterium', 'bleed', 'bleeding', 'bleeding time', 'Blood', 'blood', 'Bloody', 'burning',
              'burnings',
              'carried', 'Chronic', 'Center', 'Clearance', 'clinical diagnosis', 'Coagulation', 'coagulation',
              'complaints', 'condition', 'confirmed', 'consideration', 'Constriction', 'constriction', 
              'Consultation', 'consultation', 'consultations', 'Contact', 'contact',
              'day', 'decreas', 'decreased', 'determination', 'Development', 'development', 'diagnose', 
              'diagnosed', 'diagnosis', 'difficulty', 'disc', 'disappointment', 'Discharge',
              'discharge', 'Discharged', 'disease', 'diseases', 'disorders', 'drugs', 'dysfunction',
              'effect', 'elevation', 'emergency', 'Emotional', 'emotional', 'Erythrocytes', 'Examination', 
              'examination', 'examinations', 'Examined', 'examined', 'Exercise', 'exercises', 'extraction',
              'falls', 'field', 'first sign', 'first signs', 'Followed', 'follow-up', 'food',
              'gas', 'General', 'grade', 'gradex', 'groups',
              'Hemoglobin', 'hospitalized',
              'Improved', 'improved', 'Increased', 'injection', 'intervention', 'intolerance', 'Intolerance', 
              'irradiation', 'irritable',
              'Laboratory', 'lead increased', 'lesion', 'lesions', 'Leukocytes', 'Local', 'Low', 'low',
              'Medical', 'Medications', 'medications', 'Monitoring', 'monitoring', 'Multifocals',
              'Negative', 'negative', 'No development', 'noises', 'Nonspecific',
              'organ', 'organs', 'outpatient treatment',
              'Pain', 'pain', 'pains', 'palpation', 'pathology', 'Perform', 'Physical', 'place of residence',
              'plication', 'Positive', 'positive', 'Potassium+', 'prescribed', 'Presence', 'presence',
              'presences', 'Present', 'present', 'preserved', 'Pressure', 'pressure', 'pressures', 
              'Prevention', 'prevention', 'Prophylactic', 'Prosthesis', 'prosthesis', 'Protein', 'psych',
              'Reapplication', 'red blood cells', 'Referred', 'Reirradiation', 'Regional', 'Registered', 
              'Release', 'release', 'removal', 'Repair', 'repair', 'repairs', 'report',  'Report', 'reports',
              'resistance index', 'Result',
              'seizures', 'setting', 'Severe', 'severe', 'sharp pain', 'shortening', 'Single', 'single', 
              'Smoking', 'spells', 
              'stabilize', 'stage', 'Surgical', 'stabilized', 'study', 'surgery', 'surgical intervention', 
              'Susceptible', 'swollen', 'Symptomatic', 'syndrome',
              'Therapeutic', 'Therapy', 'therapy', 'Thoracic', 'thr', 'Thrombocytes', 'Tolerance', 'tolerance', 
              'tolerances', 'Treatment', 'treatment',
              'ultrasound', 'ultrasounds', 'Undifferentiated',
              'W exercise', 'weakness', 'weight',
              'year']

PATH_TO_MARKERS = 'markers/marker.txt'
PATH_TO_MARKERS_XLS = "markers/Molecul_Markers_of_NLP_2.xls"
SHEET_NAME = "Лист1"
URL = 'https://mtran-test.mmdx.ru/translate'

def get_translation(text, source_lang, target_lang):

    data = {"original": text, "source_lang": source_lang, "target_lang": target_lang, "content_type": "scientific"}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain',
               'X-API-KEY': '93c65fc0-c8d5-4a28-b0be-3226b2563b43'}
    r = requests.post(URL, data=json.dumps(data), headers=headers)
    result = r.json()['translation']

    return result

def matching_terms(text):
    print('MATCH START') 
    terms = matcher.match(text, best_match=True, ignore_syntax=False)
    print('MATCH END')

    return terms

def filter_terms(terms):

    selected_terms = [[x for x in group if x['similarity'] >= 0.88] for group in terms]
    selected_terms = [i for j in selected_terms for i in j]
    symptoms_and_conditions = []
    codes = ['T184', 'T047', 'T048', 'T020', 'T005', 'T007', 'T019', 'T020', 'T046', 'T049', 'T067', 'T190', 'T191']

    for term in selected_terms:
        semtypes = term['semtypes']

        for semtype in semtypes:
            if semtype in codes and term not in symptoms_and_conditions:
                symptoms_and_conditions.append(term)

    selected_terms_no_stopwords = [x for x in symptoms_and_conditions if x['term'] not in stop_words]
    tmp = []
    txt = []

    for el in selected_terms_no_stopwords:
        if el['term'].lower() not in tmp:
            tmp.append(el['term'].lower())
            txt.append(el)

    clean_terms_no_dubs = txt
    clean_terms_ranged = sorted(clean_terms_no_dubs, key=lambda i: i['start'])

    return clean_terms_ranged

import urllib.request
from datetime import datetime
import time

url = "https://raw.githubusercontent.com/dashapetrova/ma_NER/main/data/topics/topics2021.xml"
response = urllib.request.urlopen(url).read()

soup = BeautifulSoup(response, 'lxml')
matcher = QuickUMLS('/home/daria/miniconda3/quickumls')
#, threshold=0.5, similarity_name='cosine'

import json
annot_dict = {}

for tag in soup.findAll("topic"):
  print(tag["number"])
  terms = matching_terms(tag.text)
  clean_terms_ranged = filter_terms(terms)
  annot_dict[str(tag["number"])] = [clean_terms_ranged]

def set_default(obj):
  if isinstance(obj, set):
    return list(obj)
  raise TypeError
     
with open('terms_filtered_4.json', 'w') as f:
  json.dump(annot_dict, f, default=set_default)