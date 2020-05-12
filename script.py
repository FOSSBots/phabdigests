import requests
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

file = open('<config file>', 'r')
for line in file:
    info = line.split(',')
    data = {
      'api.token': '<redacted>',
      'queryKey': info[1]
    }

    response = requests.post('https://phabricator.wikimedia.org/api/maniphest.search', data=data)
    response = response.json()
    result = response["result"]
    data = result["data"]
    x = 0
    output = ''
    while x < len(data):
        parse = data[x]
        description = parse["fields"]
        description = description["name"]
        output = output + "\nhttps://phabricator.wikimedia.org/T" + str(parse["id"]) + " - " + str(description)
        output = str(output)
        x = x + 1
    msg = MIMEMultipart()
    msg["Subject"] = "Phabricator Search Alert"
    msg["From"] = "tools.phabsearchemail@tools.wmflabs.org"
    msg["To"] = info[2]
    body = "This is your automated search alert from Wikimedia Phabricator \n " + output
    msg.attach(MIMEText(body, 'plain'))

    smtp = smtplib.SMTP("localhost")
    smtp.sendmail(msg["From"], msg["To"], msg.as_string())
    smtp.quit()
    print ("Successfully sent email")
file.close()
