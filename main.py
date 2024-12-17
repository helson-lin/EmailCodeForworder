import threading

from imapclient import IMAPClient
import pyzmail
import re
import requests
import yaml
import time
import os

BARK = None

def read_config():
    if os.path.exists('config.yaml') == False:
        print("未找到配置文件，请先配置")
        exit(1)
    else:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return config

def check_config():
    os.path

def notify(title, body):
    if BARK is not None:
        # 检查 BARK 是否为列表
        if isinstance(BARK, list):
            for url in BARK:
                request_url = url.replace('$TITLE$', title).replace('$CONTENT$', body)
                try:
                    res = requests.get(request_url)
                    if res.status_code == 200:
                        print(f"通知成功: {url}")
                    else:
                        print(f"通知失败: {url}")
                except requests.RequestException as e:
                    print(f"通知请求失败 ({url}): {e}")
        else:
            # 如果 BARK 不是列表，直接发送通知
            request_url = BARK.replace('$TITLE$', title).replace('$CONTENT$', body)
            try:
                res = requests.get(request_url)
                if res.status_code == 200:
                    print("通知成功")
                else:
                    print("通知失败")
            except requests.RequestException as e:
                print(f"通知请求失败: {e}")

def listen_email(host, imap_port, username, password, use_tls=True):
    with IMAPClient(host=host, ssl=use_tls, port=imap_port, timeout=1000) as client:
        try:
            client.login(username, password)
            client.id_({"name": "IMAPClient", "version": "2.1.0"})
            print(f"{username}: Logged in Success")
            client.select_folder('INBOX')

            while True:
                messages = client.search(['NOT', 'SEEN'], charset='UTF-8')
                # print(f"Found {len(messages)} unseen messages")

                for msg_id in messages[:30]:  # 处理前 30 封邮件
                    raw_message = client.fetch(msg_id, ['BODY[]', 'ENVELOPE'])
                    email_message = pyzmail.PyzMessage.factory(raw_message[msg_id][b'BODY[]'])

                    subject = email_message.get_subject()
                    from_address = email_message.get_addresses('from')
                    text_content = email_message.text_part.get_payload().decode(email_message.text_part.charset) if email_message.text_part else "No text content"

                    if "验证码" in text_content:
                        match = re.search(r'\b(\d{6})\b', text_content)
                        if match:
                            verification_code = match.group(1)
                            title = f"来自 {from_address[0][0]} 的验证码"
                            body = verification_code
                            notify(title, body)

                # 等待一段时间再检查新邮件
                time.sleep(10)  # 每10秒检查一次
        except Exception as e:
            print(f"处理邮件时发生错误: {e}")

def start():
    global BARK
    config = read_config()
    emails = config['emails']
    BARK = config['bark']
    # 创建线程来监听每个邮箱
    threads = []
    for email in emails:
        thread = threading.Thread(target=listen_email,
                                  args=(email['host'], email['port'], email['username'], email['password']))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    try:
        start()
    except Exception as e:
        print(f"程序运行失败: {e}")
