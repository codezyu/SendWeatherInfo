import requests
import csv
import smtplib
import os
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import schedule
import time
def SetParams(city,key):
    params = {
        'location': city,
        'key': key
    }
    return params
def GetLocationID(r):
    info=r['location']
    id=info[0]['id']
    return id
def GetWeather(urlList,key,city):
    cityPar=SetParams(city,key)
    r = requests.get(urlList[0][0], params=cityPar)
    id=GetLocationID(r.json())
    weatherPar=SetParams(id,key)
    r1=requests.get(urlList[1][0], params=weatherPar)
    r2 = requests.get(urlList[2][0], params=weatherPar)
    w1=r2.json()['daily'][0]
    w=r1.json()['now']
    print(w1)
    context="当前温度为: "+w['temp']+"度"\
    +"\n 体感温度为： "+w['feelsLike']+"度"\
    +"\n 天气为： "+w['text'] \
    + "\n" + "日出时间： " + w1['sunrise'] \
    +"\n"+w['windDir']+",风力等级为: "+w1['windScaleDay']\
    +"\n"+"当日最高温度: "+w1['tempMax']\
    +"\n"+"当日最低温度: "+w1['tempMin']\
    +"\n"+"今夜为： （如果你能看到月亮）"+w1['moonPhase']\
    +"\n"+"月升时间为： "+w1['moonrise']\
    +"\n"+"晚上天气为: "+w1['textNight']
    print(context)
    return context
def GetSentence(url,header):
    r=requests.get(url,headers=header)
    s=r.json()['data']['content']
    return s
def SendEmail(to,context,title):
    msg = MIMEMultipart('mixed')
    message=MIMEText(context,'plain','utf-8')
    csv_reader = csv.reader(open("mail.csv"))
    urlList = []
    for line1 in csv_reader:
        urlList.append(line1)
    mail_host=urlList[0][0]
    mail_user=urlList[1][0]
    mail_pass=urlList[2][0]
    msg['From']=mail_user
    msg['To']=to
    msg['Subject'] = Header(title, 'utf-8').encode()
    msg.attach(message)
    print(to)
    try:
        smtpObj = smtplib.SMTP()
        # 连接到服务器
        smtpObj.connect(mail_host, 25)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            mail_user, to, msg.as_string())
        # 退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误
def job():
    csv_reader1 = csv.reader(open("city.csv",encoding="utf-8"))
    key = '86815c8e4fc44d9484fc0721518ed7aa'
    token= 'mdew4/45duV2C9pfW93cOkM3MNx7kXXm'
    for line in csv_reader1:
        csv_reader = csv.reader(open("url.csv"))
        urlList=[]
        for line1 in csv_reader:
            urlList.append(line1)
        content=GetWeather(urlList,key,line[0][0])
        header={'X-User-Token':token}
        title=GetSentence(urlList[3][0],header)
        SendEmail(line[1],content,title)
if __name__ == "__main__":
    code_dir = os.path.dirname(__file__)
    os.chdir(code_dir)
    job()
    schedule.every().day.at("06:30").do(job)
    schedule.every().day.at("14:00").do(job)
    schedule.every().day.at("18:00").do(job)
    print(os.getcwd())
    while True:
        schedule.run_pending()  # 运行所有可以运行的任务
        time.sleep(1)