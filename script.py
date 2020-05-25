import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
def run(config):
  file = open('config.csv', 'r')
  apikey = ''
  phaburl = 'phabricator.wikimedia.org'
  sender = ''
  for line in file:
    configdata = line.split(',')
    if configdata[1] == 'apikey':
      apikey = configdata[2]
    if configdata[1] == 'phaburl':
      phaburl = configdata[2]
    if configdata[1] == 'sender':
      sender = configdata[2]
  file = open(config, 'r')
  for line in file:
      info = line.split(',')
      data = {
        'api.token': apikey,
        'queryKey': info[1]
      }
      response = requests.post('https://' + phaburl + '/api/maniphest.search', data=data)
      response = response.json()
      result = response["result"]
      data = result["data"]
      x = 0
      output = ''
      while x < len(data):
          parse = data[x]
          description = parse["fields"]
          description = description["name"]
          output = output + "\n\nhttps://" + phaburl + "/T" + str(parse["id"]) + " - " + str(description)
          output = str(output)
          x = x + 1
      msg = MIMEMultipart()
      msg["Subject"] = "Phabricator Search Alert"
      msg["From"] = sender
      msg["To"] = info[2]
      body = "This is your automated search alert from Phabricator \n " + output
      msg.attach(MIMEText(body, 'plain'))
      smtp = smtplib.SMTP("localhost")
      smtp.sendmail(msg["From"], msg["To"], msg.as_string())
      smtp.quit()
      print ("Successfully sent email")
  file.close()
try:
  if sys.argv[1] == 'weekly':
    run('weekly.csv')
  elif sys.argv[1] == 'monthly':
    run('monthly.csv')
  else:
    run(sys.argv[1])
except IndexError:
 print("No command specified.")
