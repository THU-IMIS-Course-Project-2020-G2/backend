import requests, dicttoxml, xmltodict
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom.minidom import parseString 
import glob
import os, json
import time
# xml 自动化本地测试框架
filepath = 'G2/'
base_url = 'http://127.0.0.1:8000/'

xml_list = glob.glob(os.path.join(filepath, '*.xml'))
for i in range(200,300):
    #print(xml_list)
    time.sleep(0.02)
    xml_file = open(xml_list[i], 'r')
    xml_str = xml_file.read()
    #print(type(xml_str))
    title_content = xml_list[i][12:-4]
    str_url = base_url + title_content

    if title_content == 'dish_residue':    
        response = requests.get(str_url, xml_str)
    else:
        response = requests.post(str_url, xml_str)
    print(xml_list[i][3:12], 'receive successfully!')
    #if xml_list[i][12]
    jsonstr = xmltodict.parse(response.text)
    jsonstr = json.dumps(jsonstr)
    #print(json.loads(jsonstr)['root'])