# -*- coding: utf-8 -*-
from smtplib import SMTP_SSL
from email.mime.text import MIMEText


def send_mail(subject, content, dst_emails, smtp_config=None):
    if not dst_emails:
        return
    if not smtp_config:
        smtp_config = {
            'host': 'smtp.exmail.qq.com',
            'port': 465,
            'user_account': '',
            'password': '',
            'user_name': '',
            'timeout': 20
        }
    host_info = {'host': smtp_config['host']}
    port = int(smtp_config.get('port', 0))
    if port:
        host_info['port'] = port
    local_hostname = smtp_config.get('local_hostname')
    if local_hostname:
        host_info['local_hostname'] = local_hostname
    timeout = int(smtp_config.get('timeout', 0))
    if timeout:
        host_info['timeout'] = timeout
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    user_name = '%s<%s>' % (smtp_config.get('user_name', ''), smtp_config['user_account'])
    msg['From'] = user_name
    msg['Subject'] = subject
    msg['To'] = ';'.join(dst_emails)
    smtp = SMTP_SSL(**host_info)
    smtp.login(smtp_config['user_account'], smtp_config['password'])
    smtp.sendmail(user_name, dst_emails, msg.as_string())
    smtp.quit()


def main():
    while True:
        error = raw_input()
        print error
        send_mail('hello', error, [])


if __name__ == '__main__':
    main()
