# -*- coding: utf-8 -*-
from smtplib import SMTP_SSL
from email.mime.text import MIMEText

DEFAULT_SMTP_CONFIG = {
    'host': 'smtp.exmail.qq.com',
    'port': 465,
    'account': 'xxx@yyy.zzz',
    'password': '',
    'sender': 'name to show',
    'timeout': 10,
}


def send_mail(subject, content, dst_emails, smtp_config=DEFAULT_SMTP_CONFIG):
    if not dst_emails:
        return
    if not smtp_config:
        return
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
    user_name = '%s<%s>' % (smtp_config.get('sender', ''), smtp_config['account'])
    msg['From'] = user_name
    msg['Subject'] = subject
    msg['To'] = ';'.join(dst_emails)
    smtp = SMTP_SSL(**host_info)
    smtp.login(smtp_config['account'], smtp_config['password'])
    smtp.sendmail(user_name, dst_emails, msg.as_string())
    smtp.quit()
