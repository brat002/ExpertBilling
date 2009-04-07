 #-*- coding=UTF-8 -*-


"""
1001 - Запрос авторизации клиентом
1002 - Ответ с challenge строкой
1003 - Ответ на авторизацию с шифрованнымv challenge данынми абонента
1004 - Авторизация прошла успешно
1005 - неправильный пароль
1006 - несуществующий логин
1007 - Серер занят
1008 - неизвестная сессия. Запросить клиентом повторную авторизацию
1009 - запрос баланса
1010 - ответ по балансу
1011 - запрос остатка на предоплаченный трафик
1012 - ответ на запрос по предоплаченному трафику
1013 - запрос остатка на предоплаченное время
1014 - ответ по остатку на предоплаченное время
1015 - logout
1016 - logout success
 
auth
{
    client{
    [1001, len_login, login]
    }
    server
    {
    [1002, challenge 32bytes] OR [1006] OR [1007]
    }
    client{
    [1003, len_login, login,  crypt_string MD5HEXDIGEST(login+password+challenge)]
    }
    server{
    [1004, session_id 32 bytes] OR [1005] OR [1007]
    }
}

ballance{
    client{
    [1009, session_id]
    }
    server{
    [1010, ballance float 32bytes] OR [1008] OR [1007]
    }
}

prepaid traffic (остаток предоплаченного трафика)
{
    client{
    [1011, session_id]
    }
    server{
    [1012, res_length N bytes, concatenated_string имя группы<-->Всего<>Осталось<->имя группы<-->Всего<>остаток трафика и т.д.] - нужно будет распарсить OR [1008] OR [1007]
    }
}

prepaid time (остаток предоплаченного времени)
{
    client{
    [1013, session_id]
    }
    server{
    [1014, int 32 bytes] OR [1008] OR [1007]
    }
}

Остаток по лимитам в группе
{
    client{
    [1015, session_id]
    }
    server {
    [1016] OR [1008] OR [1007]
    }
}
"""


import socket, sys, time, struct, md5

host = "127.0.0.1"
textport = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = textport

testlogin = "sasha"
testpassword = "12345"
accounts_buf = {}
session_buf = {}
s.bind((host, port))
while 1:
    buf, addrport = s.recvfrom(1024)

    id, = struct.unpack("!I", buf[:4])
    if id == 1001:
        username_len, =struct.unpack("!I", buf[4:8])
        login, = struct.unpack("!%ds" % username_len, buf[8:])
        if login == testlogin:
            challenge = "12345678901234567890123456789012"
            data = struct.pack("!I32s", 1002, challenge)
            s.sendto(data, addrport)
            accounts_buf["%s" % login] = [challenge,""]
        else:
            data = struct.pack("!I", 1006)
            
    if id == 1003:
        username_len, =struct.unpack("!I", buf[4:8])
        login, = struct.unpack("!%ds" % username_len, buf[8:8+username_len])
        session_id = accounts_buf.get("%s" % login)

        if session_id:
            
            hash, = struct.unpack("!32s", buf[8+username_len:8+username_len+32])

            server_side_hash = md5.new("%s%s%s" % (login, testpassword, session_id[0])).hexdigest()
            if hash == server_side_hash:
                account_session_id = "22345678901234567890123456789012"
                data = struct.pack("!I32s", 1004, account_session_id)
                accounts_buf["%s" % login][1]=account_session_id
                session_buf[account_session_id] = login
                print "Access Allow"
            else:
                data = struct.pack("!I", 1005)
                print "Password incorrect"
        else:
            data = struct.pack("!I", 1008)
            print "Unknown Account"
        s.sendto(data, addrport)
        
    if id == 1009:
        session, =struct.unpack("!32s", buf[4:])
        session_id = session_buf.get("%s" % session)

        if session_id:
            data = struct.pack("!I32s", 1010, "1003456.65")
            s.sendto(data, addrport)
            
            
    
    
