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
    [1003, len_login, login, crypt_string MD5HEXDIGEST(login+password+challenge)]
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
    [1010, ballance str 32bytes] OR [1008] OR [1007]
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

from socket import *
import struct, md5, sys

# Set the socket parameters
host = "127.0.0.1"
port = 9090
buf = 1024
addr = (host,port)

# Create socket
UDPSock = socket(AF_INET,SOCK_DGRAM)

login = "sasha"
password = "12345"

#auth
data = struct.pack("!II%ds" % len(login), 1001, len(login), login)
#print data
UDPSock.sendto(data,addr)

data, addrport = UDPSock.recvfrom(1024)
code, = struct.unpack("!I", data[:4])
if code==1002:
    challenge, = struct.unpack("!32s", data[4:])
    print challenge

    #[1003, len_login, login, crypt_string MD5HEXDIGEST(login+password+challenge)]
    h = md5.new("%s%s%s" % (login, password, challenge)).hexdigest()

    data = struct.pack("!II%ds32s" % len(login), 1003, len(login), login, h)
    UDPSock.sendto(data,addr)
else:
    print "Auth not allowed, code", code
    sys.exit(1)
 
data, addrport = UDPSock.recvfrom(1024)
code, = struct.unpack("!I", data[:4])
print "code", code
if code==1004:
    session_id, = struct.unpack("!32s", data[4:])
    print "session_id=", session_id
else:
    print "Auth not allowed(Bad Pass), code", code 

data = struct.pack("!I32s", 1009, session_id)
UDPSock.sendto(data,addr)
    
data, addrport = UDPSock.recvfrom(1024)
code, = struct.unpack("!I", data[:4])
print "code", code
if code==1010:
    ballance, = struct.unpack("!32s", data[4:])
    print "ballance=", ballance
else:
    print "Auth not allowed(Bad Pass), code", code 
    


UDPSock.close()

