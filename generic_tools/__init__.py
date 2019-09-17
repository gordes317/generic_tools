"""
@Time:2019/9/4 16:18
@Author:jun.huang
"""
import time
import cx_Oracle
import os
import socket
import requests

# 数据库相关
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


def timestamp_to_datetime(timestamp):
    time_arr = time.localtime(int(str(timestamp)[:-3]))
    return time.strftime("%H:%M", time_arr)


def connect(username, passwd, shost):
    """连接数据库
    :param shost: 数据库地址
    :param passwd: 数据库用户密码
    :param username: 数据库用户名
    """
    conn = cx_Oracle.connect(username, passwd, shost)
    cursor = conn.cursor()
    return conn, cursor


def execute_query(cursor, sql, params=''):
    """执行sql
    :param sql: 查询sql
    :param cursor: 游标
    :param params: 参数
    """

    cursor.execute(sql, params)
    # 获取结果
    res = cursor.fetchall()
    return res


def resp_desc_query(cursor, sql, params=''):
    """执行sql
    :param params:
    :param sql:
    :param cursor:
    返回错误描述信息
    """
    cursor.execute(sql, params)
    index = cursor.description
    column_list = []
    # 获取结果
    res = cursor.fetchall()
    resp_desc_list = list()
    for i in range(len(index)):
        column_list.append(index[i][0])
    col_len = len(column_list)
    if res:
        for j in range(len(res)):
            resp_desc = dict()
            for k in range(col_len):
                try:
                    if isinstance(res[j][k], float):
                        resp_desc[column_list[k].lower()] = round(res[j][k], 2)
                    else:
                        resp_desc[column_list[k].lower()] = res[j][k]
                except KeyError:
                    resp_desc[column_list[j].lower()] = 0
            resp_desc_list.append(resp_desc)
    return resp_desc_list


def close_db(conn, cursor):
    """关闭数据库
    :param conn: 连接
    :param cursor: 游标
    """
    conn.commit()
    cursor.close()
    conn.close()


def handle_string(alarm_state, message, code_1, code_2, code_3):
    if alarm_state == "ALARM":
        level = '0|E|'
    else:
        level = '0|N|'
    str1 = level + str(code_1) + '|' + str(code_2) + '|' + str(code_3) + '|' + message.replace('<br>', '；') + '|'
    # 计算转换后的字符长度
    mes = bytes(str1, 'GBK')
    # 表示长度的字符串
    length_str = str(len(mes))
    # 没到4位在开头填充0
    for i in range(4 - len(length_str)):
        length_str = '0' + length_str
    res = length_str + str1
    return res


def socket_cli(message, code, alarm_state, socket_ip):
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(socket_ip)
        code_1 = code.split(';')[0]
        code_2 = code.split(';')[1]
        code_3 = code.split(';')[2]

        mess = handle_string(alarm_state, message, code_1, code_2, code_3)
        try:
            # 发送数据
            sk.send(bytes(mess, 'GBK'))
        except Exception as e:
            raise Exception(e)

        sk.close()
    except Exception as e:
        raise Exception(e)


class LensRoute:
    def __init__(self, **kwargs):
        """

        :param kwargs:
        ip_port: 元组类型，报警的IP,端口
        code_1,code_2,code_3:报警码
        message: 报警信息
        handle_message : 处理完的报警信息

        :return:
        """
        self.ip_port = kwargs['ip_port']
        self.code_1 = kwargs['code_1']
        self.code_2 = kwargs['code_2']
        self.code_3 = kwargs['code_3']
        self.message = kwargs['message']
        self.alarm_stat = kwargs['alarm_stat']
        self.handle_message = LensRoute.handle_string(self.alarm_stat, self.code_1,
                                                      self.code_2, self.code_3, self.message)

    def socket_send(self):
        try:
            sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 请求连接服务端
            sk.connect(self.ip_port)
        except Exception as e:
            raise Exception(e)

        try:
            # 发送数据 数据格式为00+长度+字符
            sk.send(bytes(self.handle_message, 'GBK'))
        except Exception as e:
            raise Exception(e)

        sk.close()

    @staticmethod
    def handle_string(alarm_stat, code_1, code_2, code_3, message):
        if alarm_stat == "ALARM":
            level = '0|E|'
        else:
            level = '0|N|'
        str1 = level + str(code_1) + '|' + str(code_2) + '|' + str(code_3) + '|' + message.replace('<br>', '；') + '|'
        # 计算转换后的字符长度
        mes = bytes(str1, 'GBK')
        # 表示长度的字符串
        length_str = str(len(mes))
        # 没到4位在开头填充0
        for i in range(4 - len(length_str)):
            length_str = '0' + length_str
        res = length_str + str1
        return res


class SendMsg:
    def __init__(self, title, message, token, url):
        self.title = title
        self.message = message
        self.token = token
        self.url = url

    def send(self):
        parmas = {'message': self.message, 'title': self.title, 'notifyType': 1, 'targetId': self.token,
                  'extParams': ''}
        try:
            result = requests.post(self.url, data=parmas)
            return result.text
        except Exception as e:
            raise Exception(e)


def main():
    print('hello world')

