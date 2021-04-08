import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
def run(list, phaburl):
  try:
    file = open('config.csv', 'r')
  except FileNotFoundError:
    file = open('/srv/phabdigests/config.csv', 'r')
  apikey = ''
  sender = ''
  for line in file:
    configdata = line.split(',')
    apiconfig = 'apikey-' + str(phaburl)
    if configdata[1] == apiconfig:
      apikey = configdata[2]
    if configdata[1] == 'sender':
      sender = configdata[2]
    if configdata[1] == 'emailpassword':
        gmail_password = configdata[2]
    if configdata[1] == 'replyto':
        replyto = configdata[2]
  file = open(list, 'r')
  for line in file:
      info = line.split(',')
      data = {
        'api.token': apikey,
        'queryKey': info[1]
      }
      response = requests.post('https://' + phaburl + '/api/maniphest.search', data=data)
      response = response.json()
      result = response["result"]
      try:
        data = result["data"]
      except TypeError:
        print(response)
        sys.exit(1)
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
      msg["Subject"] = "Phabricator Digests"
      msg["From"] = sender
      msg["To"] = info[2]
      msg["Reply-to"] = replyto
      body = "This is your automated search alert from Phabricator \n " + output
      msg.attach(MIMEText(body, 'plain'))
      smtp = smtplib.SMTP("mail.mirahezebots.org", 587)
      smtp.ehlo()
      smtp.starttls()
      smtp.login(sender, gmail_password)
      smtp.sendmail(msg["From"], msg["To"], msg.as_string())
      smtp.quit()
      print ("Successfully sent email")
  file.close()
try:
  if sys.argv[1] == 'weekly':
    list = 'weekly.csv'
  elif sys.argv[1] == 'monthly':
    list = 'monthly.csv'

  if sys.argv[2] == 'bots':
    phaburl = 'phab.mirahezebots.org'
  elif sys.argv[2] == 'mh':
    phaburl = 'phabricator.miraheze.org'
  run(list,phaburl)
except IndexError as e:
 print(e)
 print("Format: script.py <list> <phaburl>")
