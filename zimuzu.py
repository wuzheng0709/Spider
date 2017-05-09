#coding:utf-8
#需要安装python环境 并安装requests库

import re
import requests
import time
import json
import sys
import smtplib
from email.mime.text import MIMEText


mailto_list=["xxxx@qq.com"]    #收件箱
mail_host="smtp.163.com"         #发件箱服务器, 163的是smtp.163.com, 126的是smtp.126.com, qq的是smtp.qq.com
mail_user="xxxx"                 #发件箱用户名, 例如test@163.com, 则用户名是test
mail_pass="password"           #发件箱密码, 就是上面填的test@163.com的密码
mail_postfix="163.com"           #这个改为跟发件箱一样的后缀
zimuzu_user = "xxxx@qq.com"   #字幕组的登录邮箱
zimuzu_pass = "password"     #字幕组的登录密码
zimuzu_keyword = 'keyword'        #登录成功之后在右上角显示的用户名


def my_sleep(num):
    for i in xrange(num):
        print u'\r%s 秒'%(i+1),
        sys.stdout.flush()
        time.sleep(1)
    print u''


def login_zimuzu():
    #登录字幕组，每天登录用
    s = requests.Session()
    url = 'http://www.zimuzu.tv/User/Login/ajaxLogin'
    headers = {'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://www.zimuzu.tv',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.22 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'http://www.zimuzu.tv/user/login',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    payload = 'account=%s&password=%s&from=loginpage&remember=0&url_back='%(zimuzu_user, zimuzu_pass)
    r = s.post(url, headers=headers, data=payload)
    if zimuzu_keyword in r.headers['set-cookie']:
        print u'login_zimuzu success'
        # 签到
        r = s.get('http://www.zimuzu.tv/user/sign')
        my_sleep(15)
        r = s.get('http://www.zimuzu.tv/user/sign/dosign')
        sign_day = str(json.loads(r.content)['data'])
        r = s.get('http://www.zimuzu.tv/user/sign')
        pattern1 = re.compile('<font class="f3">(.*?)</font>')
        pattern2 = re.compile('<font class="f2">(\d{1,3})</font>')
        role = pattern1.findall(r.content)[1] #会员级别
        try:
            need_day = pattern2.search(r.content).group(1) #剩余签到天数
        except:
            need_day = '0'
        if not sign_day == '0':
            send_mail(mailto_list,'zimuzu签到成功','今日已签到。\n已连续签到 %s 天，还需 %s 天, 您现在是 %s'%(sign_day, need_day, role))
            print ('已连续签到 %s 天，还需 %s 天，您现在是 %s'%(sign_day, need_day, role)).decode('utf-8')
        else:
            send_mail(mailto_list,'zimuzu签到失败','今日签到失败.\n还需 %s 天, 您现在是 %s'%(need_day, role))
            print ('签到失败，还需 %s 天, 您现在是 %s'%(need_day, role)).decode('utf-8')
    else:
        print u'login_zimuzu fail'


def send_mail(to_list,sub,content):
    me="Python脚本"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain',_charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False


if __name__ == '__main__':
    try:
        login_zimuzu()
    except Exception,e:
        with open('zimuzu.log', 'a') as f:
            f.write(str(e)+'\n')
