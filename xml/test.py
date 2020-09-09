import requests, dicttoxml, xmltodict
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom.minidom import parseString 
import glob
import os, json
import time
# xml 自动化本地测试框架
filepath = 'xml/G2/'
base_url = 'http://124.70.178.153:8082/'

xml_list = glob.glob(os.path.join(filepath, '*.xml'))
for i in range(0, 300):
    #print(xml_list)
    time.sleep(0.01)
    xml_file = open(xml_list[i], 'r')
    xml_str = xml_file.read()
    #print(type(xml_str))
    title_content = xml_list[i][16:-4]
    str_url = base_url + title_content

    if title_content == 'dish_residue':    
        response = requests.get(str_url, xml_str)
    else:
        response = requests.post(str_url, xml_str)
        time.sleep(0.5)
    print(xml_list[i][7:16], 'receive successfully!')
    #if xml_list[i][12]
    jsonstr = xmltodict.parse(response.text)
    jsonstr = json.dumps(jsonstr)
    #print(json.loads(jsonstr)['root'])