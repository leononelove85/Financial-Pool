# encoding: utf-8
# encoding: gbk

# 因为可能会用到中文，所以必须有上面的这两句话

# 引入模块及IMAPClient类
import getpass, email, sys, re, time, os
from imapclient import IMAPClient

#i=sys.argv[1];

def decode_multiline_header(s):
    ret = []
    for b, e in email.header.decode_header(re.sub(r'\n\s+', ' ', s)):
        if e:
            if e.lower() in 'gb2312' or 'gb18030':
                b = b.decode(e)
            elif isinstance(b, bytes):
                b = b.decode('ascii')
        ret.append(b)
    return ''.join(ret)

def func(i):
    hostname = 'mail.cgws.com'  # gmail的smtp服务器网址
    username = 'lixu'
    passwd = '~~'

    c = IMAPClient(hostname, ssl=False)  # 通过一下方式连接smtp服务器，没有考虑异常情况，详细请参考官方文档
    try:
        c.login(username, passwd)  # 登录个人帐号
    except c.Error:
        print('Could not log in')
        sys.exit(1)
    else:
        c.select_folder('INBOX', readonly=True)
    # 利用select_folder()函数进行文件夹，'INBOX'为收件箱，readonly = True 表明只读并不修改任何信息
        dirtoday =  os.path.abspath(__file__) + time.strftime('%Y%m%d', time.localtime(time.time()))
        if not os.path.exists(dirtoday):
            os.makedirs(dirtoday)  # 创建当前日期目录
        sincetime = time.strftime('%d-%b-%Y', time.localtime(time.time()))  # 获取当天的搜索时间,日期格式必须是05-Jul-2017
        result = c.search('SINCE ' + sincetime)
        msgdict = c.fetch(result, ['BODY.PEEK[]'])

    # 现在已经把邮件取出来了，下面开始解析邮件
        for message_id, message in msgdict.items():
            a = message[b'BODY[]']
            e = email.message_from_bytes(message[b'BODY[]'])  # 生成Message类型
            # 由于'From', 'Subject' header有可能有中文，必须把它转化为中文
            subject = email.header.make_header(email.header.decode_header(e['SUBJECT']))
            mail_from = email.header.make_header(email.header.decode_header(e['From']))

            # 解析邮件正文
            maintype = e.get_content_maintype()
            mail_content = b''
            if maintype == 'multipart':
                for part in e.get_payload():
                    name = part.get_param("name")  # 如果是附件，这里就会取出附件的文件名
                    if name:
                        # 有附件
                        name = decode_multiline_header(name)
                        fname = dirtoday + "\\" + name
                        attach_data = part.get_payload(decode=True)  # 解码出附件数据，然后存储到文件中
                        try:
                            f = open(fname, 'wb')  # 注意一定要用wb来打开文件，因为附件一般都是二进制文件
                        except Exception as e:
                            print('附件名有非法字符，自动换一个')
                            f = open('temp1', 'wb')
                        f.write(attach_data)
                        f.close()
                    else:
                        # 不是附件，是文本内容
                        print(part.get_payload(decode=True))  # 解码出文本内容，直接输出来就可以了。
            elif maintype == 'text':
                mail_content = e.get_payload(decode=True).strip()

            # 此时，需要把content转化成中文，利用如下方法：
            try:
                mail_content = mail_content.decode('gbk')
            except UnicodeDecodeError:
                print('decode error')
                sys.exit(1)
            else:
                print('new message')
                print('From: ', mail_from)
                print('Subject: ', subject)
                
#                getstr = input('if you wanna read it, input y: ')
#                if getstr.startswith('y'):
#                    print('-'*10, 'mail content', '-'*10)
#                    print(mail_content.replace('<br>', '\n'))
#                    print('-'*10, 'mail content', '-'*10)
#                
    finally:
        c.logout()
        return len(msgdict)


func(0)
