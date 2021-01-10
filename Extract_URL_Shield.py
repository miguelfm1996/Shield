#!/usr/bin/env python3.8.2

import re
from bs4 import BeautifulSoup
import urllib3
import json
from html.parser import HTMLParser

url_base = "https://shield.mitre.org/techniques/"

techniques_relation={}



def get_techniques_ids():
    global techniques_ids
    techniques_ids = []
    http = urllib3.PoolManager()
    r = http.request('GET', "https://github.com/MITRECND/mitrecnd.github.io/raw/master/_data/techniques.json")
    if r.status == 200:
        a = json.loads(r.data)
        for i in a:
            techniques_ids.append(i['id'])


def get_html():
    global techniques_html
    techniques_html = {}
    for i in techniques_ids:
        http = urllib3.PoolManager()
        r = http.request('GET', url_base + i)
        techniques_html[i] = r.data.decode('utf-8')

def get_tactics():
    global tactics
    tactics = []
    http = urllib3.PoolManager()
    r = http.request('GET', "https://github.com/MITRECND/mitrecnd.github.io/raw/master/_data/tactics.json")
    if r.status == 200:
        a = json.loads(r.data)
        for i in a:
            tactics.append(i['name'])

def parse_html():
    for i in techniques_html:
        parsed_html_base = BeautifulSoup(techniques_html[i], 'html.parser')
        parsed_html = parsed_html_base.find_all(class_="table table-bordered table-hover")
        opportunities = []
        use_cases = []
        procedures = []
        att_tactics = []
        for j in parsed_html:
            if not opportunities:
                opportunities = re.findall("DOS.*", j.text)
            if not use_cases:
                use_cases = re.findall("DUC.*", j.text)
            if not procedures:
                procedures = re.findall("DPR.*", j.text)
            if not att_tactics:
                att_tactics = re.findall("T1.*", j.text)
        parsed_html_card = parsed_html_base.find(class_="card")
        parsed_html_card = parsed_html_card.find_all("a")
        get_tactics()
        tactics_technique = []
        for j in parsed_html_card:
            for x in tactics:
                if x in j.text:
                    tactics_technique.append(x)
        techniques_relation[i] = [tactics_technique, opportunities, use_cases, procedures, att_tactics]

def info_to_json():
    dict_list = []
    for i in techniques_relation:
        aux = {
            "technique_id":i,
            "tactics_name":techniques_relation[i][0],
            "opportunities_ids":techniques_relation[i][1],
            "use_cases_ids":techniques_relation[i][2],
            "procedures_ids":techniques_relation[i][3],
            "att_tactics_ids":techniques_relation[i][4]
        }
        dict_list.append(aux)
    with open('final.json', 'r+') as f:
        f.write(json.dumps(dict_list))

if __name__ == "__main__":
    get_techniques_ids()
    get_html()
    parse_html()
    info_to_json()