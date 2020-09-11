import requests
serve_url = 'http://124.70.178.153:8080/g1/serve'
xml_file = open('serve.xml', 'r')
xml_str = xml_file.read()
header = {'content-type':'application/xml'}
requests.post(serve_url, xml_str, headers = header)