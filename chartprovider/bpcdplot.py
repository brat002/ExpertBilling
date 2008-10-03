#-*-coding=utf-8-*-
import pychartdir
from pychartdir import *
from bpbl import bpbl, selstrdict
import sys, copy
from collections import defaultdict

portdict = {\
    '1'    : 'tcpmux', '5': 'rje', '7': 'echo', '9': 'discard', '11': 'systat', '13': 'daytime', '15': 'netstat', '17': 'qotd', '18': 'send/rwp', '19': 'chargen', '20': 'ftp-data', '21': 'ftp', '22': 'ssh, pcAnywhere',\
    '23'   : 'Telnet', '25': 'SMTP', '27': 'ETRN', '29': 'msg-icp', '31': 'msg-auth', '33': 'dsp', '37': 'time', '38': 'RAP', '39': 'rlp', '42': 'nameserv', '43': 'whois', '49': 'TACACS', '50': 'RMCP', '53': 'DNS', '57': 'MTP',\
    '59'   : 'NFILE', '63': 'whois++', '66': 'sql*net', '67': 'bootps', '68': 'bootpd/dhcp', '69': 'tftp', '70': 'Gopher', '79': 'finger', '80': 'www-http', '81': 'torpark', '88': 'Kerberos, WWW', '95': 'supdup', '96': 'DIXIE', '98': 'linuxconf',\
    '101'  : 'HOSTNAME', '102': 'ISO, X.400, ITOT', '105': 'cso', '106': 'poppassd', '109': 'POP2', '110': 'POP3', '111': 'Sun RPC Portmapper', '113': 'identd/auth', '115': 'sftp', '117': 'uucp', '119': 'NNTP', '120': 'CFDP', \
    '123'  : 'NTP', '124': 'SecureID', '129': 'PWDGEN', '133': 'statsrv', '135': 'loc-srv/epmap', '137': 'netbios-ns', '138': 'netbios-dgm (UDP)', '139': 'NetBIOS', '143': 'IMAP', '144': 'NewS', '152': 'BFTP', '153': 'SGMP', \
    '161'  : 'SNMP', '175': 'vmnet', '177': 'XDMCP', '178': 'NextStep', '179': 'BGP', '180': 'SLmail', '199': 'smux', '210': 'Z39.50', '218': 'MPP', '220': 'IMAP3', '259': 'ESRO', '264': 'FW1_topo', '311': 'Apple WA', \
    '350'  : 'MATIP type A', '351': 'MATIP type B', '363': 'RSVP tunnel', '366': 'ODMR)', '387': 'AURP', '389': 'LDAP', '407': 'Timbuktu', '412': 'DCC', '434': 'Mobile IP', '443': 'ssl/HTTPS', '444': 'snpp', '445': 'SMB', '458': 'QuickTime TV/C', \
    '468'  : 'Photuris', '500': 'ISAKMP, pluto', '512': 'biff, rexec', '513': 'who, rlogin', '514': 'syslog, rsh', '515': 'lp, lpr, line printer', '517': 'talk', '520': 'RIP', '521': 'RIPng', '522': 'ULS', '530': 'RPC', '531': 'IRC', '540': 'UUCP',\
    '543'  : 'KLogin, ASoIP', '545': 'QuickTime', '546': 'DHCPv6 cli', '547': 'DHCPv6 ser', '548': 'AFP', '554': 'RTSP', '555': 'phAse Zero', '563': 'NNTP over SSL', '575': 'VEMMI', '581': 'BDP', '593': 'MS-RPC', '608': 'SIFT/UFT', '626': 'Apple ASIA', '631': 'IPP', \
    '635'  : 'mountd', '636': 'sldap', '642': 'EMSD', '648': 'RRP ', '655': 'tinc', '660': 'Apple MacOS SA', '666': 'Doom', '674': 'ACAP', '687': 'AS IPReg', '700': 'buddyphone', '705': 'AgentX for SNMP', '901': 'swat, realsecure', \
    '993'  : 's-imap', '995': 's-pop', '1062': 'Veracity', '1080': 'SOCKS', '1085': 'WebObjects', '1227': 'DNS2Go', '1243': 'SubSeven', '1338': 'Millennium Worm', '1352': 'Lotus Notes', '1381': 'ANLM', '1417': 'Timbuktu', '1418': 'Timbuktu', '1419': 'Timbuktu', \
    '1433' : 'MSSQL Server', '1434': 'MSSQL Monitor', '1494': 'Citrix ICA', '1503': 'T.120', '1521': 'Oracle SQL', '1525': 'prospero', '1526': 'prospero', '1527': 'tlisrv', '1604': 'Citrix ICA, MS TS', '1645': 'RADIUS Auth', '1646': 'RADIUS Acc', \
    '1680' : 'Carbon Copy', '1701': 'L2TP/LSF', '1717': 'Convoy', '1720': 'H.323/Q.931', '1723': 'PPTP cport', '1755': 'WM.asf', '1758': 'TFTP mcast', '1812': 'RADIUS serv', '1813': 'RADIUS acc', '1818': 'ETFTP', '1973': 'DLSw DCAP/DRAP', '1985': 'HSRP', \
    '1999' : 'Cisco AUTH', '2001': 'glimpse', '2049': 'NFS', '2064': 'distributed.net', '2065': 'DLSw', '2066': 'DLSw', '2106': 'MZAP', '2140': 'DeepThroat', '2327': 'Netscape Conf', '2336': 'Apple UG', '2427': 'MGCP gateway', '2504': 'WLBS', '2535': 'MADCAP', \
    '2543' : 'sip', '2592': 'netrek', '2628': 'DICT', '2727': 'MGCP agent', '2998': 'ISS RSC', '3000': 'Firstclass', '3031': 'Apple AgentVU', '3128': 'web cache', '3130': 'ICP', '3150': 'DeepThroat', '3264': 'ccmail', '3283': 'Apple NA', '3288': 'COPS', '3305': 'ODETTE', \
    '3306' : 'mySQL', '3389': 'RDP', '3521': 'netrek', '3724': "WoW", '4000': 'icq, Diablo', '4321': 'rwhois', '4333': 'mSQL', '4662': 'eMule', '4827': 'HTCP', '5004': 'RTP', '5005': 'RTP', '5010': 'Y!M', '5050': 'Y!M','5060': 'SIP', '5190': 'ICQ, AIM', '5222': 'Jabber', '5432': 'PostgreSQL', '5423': 'Apple VU', '5500': 'securid', '5501': 'securidprop', '5631': 'PCAnywhere', \
    '5632' : 'PCAnywhere', '5800': 'VNC', '5801': 'VNC', '5900': 'VNC', '5901': 'VNC', '6000': 'X Windows', '6112': 'BattleNet', '6502': 'Netscape Conf', '6667': 'IRC', '6668': 'IRC', '6669': 'IRC', '6776': 'Sub7', '6970': 'RTP', '7007': 'MSBD', '7070': 'RealServer/QT', \
    '7648' : 'CU-SeeMe', '7649': 'CU-SeeMe', '7778': 'Unreal', '8010': 'WinGate 2.1', '8080': 'HTTP Proxy', '8181': 'HTTP', '8383': 'IMail WWW', '8875': 'napster', '8888': 'napster', '9050': 'tor', '10008': 'cheese worm', '11371': 'PGP5 Keyserv', '13223': 'PowWow', '13224': 'PowWow', '14237': 'Palm', '14238': 'Palm', \
    '18888': 'LiquidAudio', '21157': 'Activision', '23213': 'PowWow', '23214': 'PowWow', '23456': 'EvilFTP', '26000': 'Quake', '27001': 'QuakeWorld', '27010': 'Half-Life', '27015': 'Half-Life', '27960': 'QuakeIII', '30029': 'AOL Admin', '31337': 'Back Orifice', \
    '32773': 'rpc.ttdbserverd', '32776': 'rpc.spray', '32777': 'rpc.walld', '32779': 'rpc.cmsd', '38036': 'timestep', '40193': 'Novell', '41524': 'arcserve', '45000': 'Cisco NetRanger'\
}


class cdDrawer(object):
    cdchartoptdict = {\
        "nfs_user_traf":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Трафик", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat': '{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2,  'xaxissetlabelformat': '{value|dd.mm.yy\nhh:nn:ss}', \
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'outfill': True, \
                                         'antialias': False, \
                                         'addlinelayer_in':(0x0000FF, "INPUT"), 'setlinewidth_in':1.3, \
                                         'addlinelayer_out':(0x00cc00, "OUTPUT"), 'setlinewidth_out':1.3, \
                                         'addlinelayer_tr':(0xFF0000, "TRANSIT"), 'setlinewidth_tr':1.3},\
         "nfs_user_speed": \
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Скорость", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'outfill': True, \
                                         'antialias': False, \
                                         'addlinelayer_in': (0x0000FF, "INPUT"),   'setlinewidth_in':1.3, \
                                         'addlinelayer_out':(0x00cc00, "OUTPUT"),  'setlinewidth_out':1.3, \
                                         'addlinelayer_tr': (0xFF0000, "TRANSIT"),'setlinewidth_tr':1.3},\
        "nfs_total_users_traf":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Трафик", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'addlinelayer_total':(0x0000FF, "TOTAL"), 'setlinewidth_total':1.3},\
        "nfs_total_users_speed":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'yaxissettitle':("Скорость", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'addlinelayer_total':(0x0000FF, "TOTAL"), 'setlinewidth_total':1.3},\
        "nfs_total_traf_bydir":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Трафик", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat': '{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2,  'xaxissetlabelformat': '', \
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'outfill': True, \
                                         'antialias': False, \
                                         'addlinelayer_in': (0x0000FF, "INPUT"),   'setlinewidth_in':1.3, \
                                         'addlinelayer_out':(0x00cc00, "OUTPUT"),  'setlinewidth_out':1.3, \
                                         'addlinelayer_tr': (0xFF0000, "TRANSIT"),'setlinewidth_tr':1.3},\
        "nfs_total_speed_bydir":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Скорость", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'outfill': True, \
                                         'antialias': False, \
                                         'addlinelayer_in': (0x0000FF, "INPUT"),   'setlinewidth_in':1.3, \
                                         'addlinelayer_out':(0x00cc00, "OUTPUT"),  'setlinewidth_out':1.3, \
                                         'addlinelayer_tr': (0xFF0000, "TRANSIT"),'setlinewidth_tr':1.3},\
        "nfs_total_traf":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'yaxissettitle':("Трафик", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'addlinelayer_total':(0x0000FF, "TOTAL"), 'setlinewidth_total':1.3},\
        "nfs_total_speed":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'yaxissettitle':("Скорость", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'addlinelayer_total':(0x0000FF, "TOTAL"), 'setlinewidth_total':2},\
        "nfs_port_speed": \
                                        {'xychart':(800, 450), 'setplotarea':(100, 85, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(50, 30, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':["Скорость по %s порту:", "fonts/LiberationMono-Regular.ttf", 18], \
                                         'yaxissettitle':("Скорость", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'outfill': True, \
                                         'antialias': False, \
                                         'addlinelayer_in': (0x0000FF, "INPUT"),   'setlinewidth_in':1.3, \
                                         'addlinelayer_out':(0x00cc00, "OUTPUT"),  'setlinewidth_out':1.3, \
                                         'addlinelayer_tr': (0xFF0000, "TRANSIT"),'setlinewidth_tr':1.3}, \
        "nfs_nas_traf":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Трафик", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat': '{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2,  'xaxissetlabelformat': '', \
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'outfill': True, \
                                         'antialias': False, \
                                         'addlinelayer_in':(0x0000FF, "INPUT"), 'setlinewidth_in':1.3, \
                                         'addlinelayer_out':(0x00cc00, "OUTPUT"), 'setlinewidth_out':1.3, \
                                         'addlinelayer_tr':(0xFF0000, "TRANSIT"), 'setlinewidth_tr':1.3},\
        "nfs_total_nass_traf":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(90, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Трафик", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'addlinelayer_total':(0x0000FF, "TOTAL"), 'setlinewidth_total':1.3},\
        "nfs_total_classes_speed":\
                                        {'xychart':(800, 300), 'setplotarea':(100, 45, 650, 200, 0xffffff, -1, 0xc0c0c0, 0xc0c0c0, -1), 'setcolors':pychartdir.defaultPalette, \
                                         'addlegend':(30, 0, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,  'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), \
                                         'yaxissettitle':("Трафик", "fonts/LiberationMono-Regular.ttf", 18), 'yaxissetwidth':2, 'yaxissetlabelformat':'{value|2.}',\
                                         'xaxissettitle':("Время", "fonts/LiberationMono-Regular.ttf", 14), 'xaxissetwidth':2, 'xaxissetlabelformat':'',\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'addlinelayer_total':(0x0000FF, "TOTAL"), 'setlinewidth_total':1.3},\
        "userstrafpie":     \
                                        {'piechart':(600, 280), 'setpiesize': (300, 120, 110), 'addtitle': ('', "fonts/LiberationMono-Regular.ttf", 14), 'setlabelstyle':("fonts/LiberationMono-Regular.ttf",)}, \
        "sessions":  \
                                        {'xychart':(800, 280), 'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), 'setplotarea':(120, 40, 620, 220, 0xffffff, -1, -1, 0xc0c0c0, 0xc0c0c0), \
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'settickoffset':0.5, 'addboxwhiskersess':(None, None, None, 0x366e97, pychartdir.SameAsMainColor, pychartdir.SameAsMainColor), 'dashlinecolor':(0xff0000, DashLine)}, \
        "trans_deb": \
                                        {'xychart':(620, 310), 'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), 'setplotarea':(140, 55, 460, 200, 0xffffff, -1, -1, 0xa2c5de, 0xa2c5de), \
                                         'setcolors':pychartdir.defaultPalette, 'addlegend':(150, 20, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'addlinelayer_trans': (0x0000FF,), 'addscatterlayer': ("Sum", pychartdir.DiamondSymbol, 13, 0x0000FF),  'setlinewidth_trans':2, \
                                         'settickoffset':0.5, 'addbarlayer':(-1, '', 0), 'yaxissetlabelformat':'{value}', 'currency':''}, \
        "trans_crd":  \
                                        {'xychart':(620, 310), 'addtitle':("", "fonts/LiberationMono-Regular.ttf", 18), 'setplotarea':(140, 55, 460, 200, 0xffffff, -1, -1, 0xc0c0c0, 0xc0c0c0), \
                                         'setcolors':pychartdir.defaultPalette, 'addlegend':(150, 20, 0, "fonts/LiberationMono-Regular.ttf", 14), 'legendbackground':pychartdir.Transparent,\
                                         'xaxissetlabelstyle':("fonts/LiberationMono-Regular.ttf",), 'yaxissetlabelstyle': ("fonts/LiberationMono-Regular.ttf",), \
                                         'autoticks': False, \
                                         'antialias': False, \
                                         'addlinelayer_trans': (0x0000FF,), 'addscatterlayer': ("Sum", pychartdir.DiamondSymbol, 13, 0x0000FF),  'setlinewidth_trans':2, \
                                         'settickoffset':0.5, 'addbarlayer':(-1, '', 0), 'yaxissetlabelformat':'{value}', 'currency':''}
                                }



    def __init__(self):
        pychartdir.setLicenseCode("ME7YWN3DBFQU2C7MB3971677")
        #self.defoptdict = copy.deepcopy(self.cdchartoptdict)
    def cddraw(self, *args, **kwargs):
        '''Plotting methods' handler
	@args[0] - method identifier'''
        methodName = self.translate_args(*args, **kwargs)
        print args
        print methodName
        method = getattr(self, "cddraw_" + methodName, None)
        if callable(method):
            self.set_options(methodName, kwargs['options'])
            args = args[1:]
            res =  method(*args, **kwargs)
            res.append(kwargs['return'])
            return res
        else:
            raise Exception("Plotting method #" + args[0] + "# does not exist!" )


    def cddraw_nfs_user_traf(self, *args, **kwargs):
        try:

            #get a string from #selstrdict# dictionary with a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', direction', '(account_id=%d) AND' % kwargs['users'][0], args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' ')))
            print selstr
        except Exception, ex:
            raise ex
        data = bpbl.get_traf(selstr, kwargs.has_key('sec') and kwargs['sec'])	
        if not data: print "Dataset is empty"; data = ([], [], [], [], '', 1)
        (times, y_in, y_out, y_tr, bstr, sec) = data 
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_user_traf']

        retlist = []
        c = XYChart(*optdict['xychart'])

        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)

        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])

        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']:
            c.xAxis().setFormatCondition("align", 31104000)	    
            c.xAxis().setLabelFormat("{value|yy}")

            delim = "/"

            ddLoc = optdict['xaxissetlabelformat'].find("dd")	    
            if ddLoc != -1:
                delim = optdict['xaxissetlabelformat'][ddLoc + 2]

            c.xAxis().setFormatCondition("align", 2592000)
            c.xAxis().setLabelFormat("{value|mm" + delim + "yy}")

            c.xAxis().setFormatCondition("align", 86400)
            c.xAxis().setLabelFormat("{value|dd" + delim + "mm" + delim + "yy}")

            c.xAxis().setFormatCondition("else")
            c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])




        #if optdict['outfill']:
            # Add out line layer
            #layer_out = c.addDataLayer(y_out, *optdict['addlinelayer_out'])
            #layer_out.setXData(times)     
            #layer_out.setLineWidth(optdict['setlinewidth_out'])

        # Add in line layer 
        layer_in = c.addLineLayer(y_in, *optdict['addlinelayer_in'])
        layer_in.setXData(times)        
        # Set the line width 
        layer_in.setLineWidth(optdict['setlinewidth_in'])        

        # Add out line layer
        layer_out = c.addAreaLayer(y_out, *optdict['addlinelayer_out'])
        layer_out.setXData(times)     
        layer_out.setLineWidth(optdict['setlinewidth_out'])
        layer_out.setBorderColor(optdict['addlinelayer_out'][0])

        '''# Add tr line layer
	layer_tr = c.addLineLayer(y_tr, *optdict['addlinelayer_tr'])
        layer_tr.setXData(times)        
        # Set the line width
        layer_tr.setLineWidth(optdict['setlinewidth_tr'])'''

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def cddraw_nfs_user_speed(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', direction', '(account_id=%d) AND' % kwargs['users'][0], args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' ')))
        except Exception, ex:
            raise ex
        data = bpbl.get_speed(selstr, kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], [], [], '', 1)
        (times, y_in, y_out, y_tr, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_user_speed']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])

        # Add in line layer 
        layer_in = c.addLineLayer(y_in, *optdict['addlinelayer_in'])
        layer_in.setXData(times)        
        # Set the line width 
        layer_in.setLineWidth(optdict['setlinewidth_in'])        

        # Add out line layer
        layer_out = c.addAreaLayer(y_out, *optdict['addlinelayer_out'])
        layer_out.setXData(times)     
        layer_out.setLineWidth(optdict['setlinewidth_out'])
        layer_out.setBorderColor(optdict['addlinelayer_out'][0])

        '''# Add tr line layer
	layer_tr = c.addLineLayer(y_tr, *optdict['addlinelayer_tr'])
        layer_tr.setXData(times)        
        # Set the line width
        layer_tr.setLineWidth(optdict['setlinewidth_tr'])'''
        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def cddraw_nfs_total_traf_bydir(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', direction', '',  args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' ')))
        except Exception, ex:
            raise ex
        data = bpbl.get_traf(selstr, kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], [], [], '', 1)
        (times, y_in, y_out, y_tr, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_traf_bydir']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 10)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])

        # Add in line layer 
        layer_in = c.addLineLayer(y_in, *optdict['addlinelayer_in'])
        layer_in.setXData(times)        
        # Set the line width 
        layer_in.setLineWidth(optdict['setlinewidth_in'])        

        # Add out line layer
        layer_out = c.addLineLayer(y_out, *optdict['addlinelayer_out'])
        layer_out.setXData(times)     
        layer_out.setLineWidth(optdict['setlinewidth_out'])

        '''# Add tr line layer
	layer_tr = c.addLineLayer(y_tr, *optdict['addlinelayer_tr'])
        layer_tr.setXData(times)        
        # Set the line width
        layer_tr.setLineWidth(optdict['setlinewidth_tr'])
	'''
        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist


    def cddraw_nfs_total_speed_bydir(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', direction', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' ')))
        except Exception, ex:
            raise ex
        data = bpbl.get_speed(selstr, kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], [], [], '', 1)
        (times, y_in, y_out, y_tr, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_speed_bydir']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 10)
            c.yAxis().setTickDensity(yplen / 5, yplen / 10)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])

        # Add in line layer 
        layer_in = c.addLineLayer(y_in, *optdict['addlinelayer_in'])
        layer_in.setXData(times)        
        # Set the line width 
        layer_in.setLineWidth(optdict['setlinewidth_in'])        

        # Add out line layer
        layer_out = c.addLineLayer(y_out, *optdict['addlinelayer_out'])
        layer_out.setXData(times)     
        layer_out.setLineWidth(optdict['setlinewidth_out'])

        '''# Add tr line layer
	layer_tr = c.addLineLayer(y_tr, *optdict['addlinelayer_tr'])
        layer_tr.setXData(times)        
        # Set the line width
        layer_tr.setLineWidth(optdict['setlinewidth_tr'])'''
        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist


    def cddraw_nfs_total_users_traf(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', account_id', "(account_id IN (%s)) AND" % ', '.join([str(int) for int in kwargs['users']]), args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' ')))
            print selstr
        except Exception, ex:
            print "Query exception!"
            print ex
            raise ex
        data = bpbl.get_total_users_traf(selstr, kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, y_total_u, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_users_traf']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])


        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['usernames'] % ("IN (%s)" % ', '.join([str(int) for int in kwargs['users']]))
        except Exception, ex:
            raise ex
        data = bpbl.get_usernames(selstr)
        if not data: print "Dataset is empty"; return []

        #for key in y_total_u.iterkeys():
            #layer = c.addLineLayer(y_total_u[key], -1, key)
            #layer.setXData(times)        
            ## Set the line width	
            #layer.setLineWidth(optdict['setlinewidth_total'])
        # Add in line layer 
        print "data------------------------"
        print data
        for tuple in data:
            try:
                layer = c.addLineLayer(y_total_u[str(tuple[1])], -1, tuple[0].encode('utf-8'))
                layer.setXData(times)        
                # Set the line width	
                layer.setLineWidth(optdict['setlinewidth_total'])
            except Exception, ex:
                print ex 

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist


    def cddraw_nfs_total_users_speed(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', account_id', "(account_id IN (%s)) AND" % ', '.join([str(int) for int in kwargs['users']]), args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' ')))
        except Exception, ex:
            raise ex
        data = bpbl.get_total_users_speed(selstr, kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, y_total_u, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_users_speed']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])

        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['usernames'] % ("IN (%s)" % ', '.join([str(int) for int in args[0]]))
        except Exception, ex:
            raise ex
        data = bpbl.get_usernames(selstr)
        if not data: print "Dataset is empty"; return []

        #for key in y_total_u.iterkeys():
            #layer = c.addLineLayer(y_total_u[key], -1, key)
            #layer.setXData(times)        
            ## Set the line width	
            #layer.setLineWidth(optdict['setlinewidth_total'])
        # Add in line layer 
        for tuple in data:
            try:
                layer = c.addLineLayer(y_total_u[str(tuple[1])], -1, tuple[0].encode('utf-8'))
                layer.setXData(times)        
                # Set the line width	
                layer.setLineWidth(optdict['setlinewidth_total'])
            except Exception, ex:
                print ex    

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist


    def cddraw_nfs_total_traf(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % ('', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' '))\
                                      )
        except Exception, ex:
            raise ex
        data = bpbl.get_total_traf(selstr, kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, y_total, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_traf']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])

        # Add in line layer 
        layer_in = c.addLineLayer(y_total, *optdict['addlinelayer_total'])
        layer_in.setXData(times)        
        # Set the line width 
        layer_in.setLineWidth(optdict['setlinewidth_total'])        

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def cddraw_nfs_total_speed(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % ('', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' '))\
                                      )
        except Exception, ex:
            raise ex
        data = bpbl.get_total_speed(selstr, kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, y_total, bstr, sec) = data 
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_speed']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])

        # Add in line layer 
        layer_in = c.addLineLayer(y_total, *optdict['addlinelayer_total'])
        layer_in.setXData(times)        
        # Set the line width 
        layer_in.setLineWidth(optdict['setlinewidth_total'])        

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist


    def cddraw_nfs_port_speed(self, *args, **kwargs):
        try:
            pts = ', '.join(str(pint) for pint in kwargs['ports'])
            selstr = selstrdict['nfs_port_speed'] % (pts, pts, args[0].isoformat(' '), args[1].isoformat(' '))
        except Exception, ex:
            raise ex
        data = bpbl.get_port_speed(selstr, kwargs['ports'], kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], {'0':[{'input': [], 'output': [], 'transit': []}]}, '', 1)
        (times, y_ps, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_port_speed']
        retlist = []

        for ykey in y_ps.iterkeys():
            c = XYChart(*optdict['xychart']) 
            if not optdict['antialias']:
                c.setAntiAlias(0)
            c.setPlotArea(*optdict['setplotarea'])
            c.setColors(optdict['setcolors'])
            c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

            if not optdict['autoticks']:
                xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
                yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
                c.xAxis().setTickDensity(yplen / 5, yplen / 10)
                c.yAxis().setTickDensity(yplen / 5, yplen / 10)
            # Add a title to the chart 
            #titlelist = optdict['addtitle']
            titlestr  =  optdict['addtitle'][0] % ((portdict.has_key(ykey) and (ykey + ' (' + portdict[ykey] + ')')) or ykey)
            c.addTitle(titlestr, *optdict['addtitle'][1:])        
            # Add a title to the y axis 
            c.yAxis().setTitle(*optdict['yaxissettitle'])        
            # Set the y axis line width 
            c.yAxis().setWidth(optdict['yaxissetwidth'])        
            # Add a title to the x axis 
            c.xAxis().setTitle(*optdict['xaxissettitle'])        
            # Set the x axis line width
            c.xAxis().setWidth(optdict['xaxissetwidth'])
            #-----------------
            c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
            c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
            #-----------------
            c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr[ykey])
            #-----------------
            if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])
            #------------------
            # Add in line layer 
            '''layer_ins = c.addLineLayer(y_ps[ykey]['input'], *optdict['addlinelayer_ins'])
	    layer_ins.setXData(times)        
	    # Set the line width 
	    layer_ins.setLineWidth(optdict['setlinewidth_ins'])  
	    # Add out line layer
	    layer_outs = c.addLineLayer(y_ps[ykey][0]['output'], *optdict['addlinelayer_outs'])
	    layer_outs.setXData(times)     
	    layer_outs.setLineWidth(optdict['setlinewidth_outs'])	    
	    # Add in line layer 
	    layer_ind = c.addLineLayer(y_ps[ykey][1]['input'], *optdict['addlinelayer_ind'])
	    layer_ind.setXData(times)        
	    # Set the line width 
	    layer_ind.setLineWidth(optdict['setlinewidth_ind'])	    
	    # Add out line layer
	    layer_outd = c.addLineLayer(y_ps[ykey][1]['output'], *optdict['addlinelayer_outd'])
	    layer_outd.setXData(times)     
	    layer_outd.setLineWidth(optdict['setlinewidth_outd'])'''

            # Add in line layer 
            layer_in = c.addLineLayer(y_ps[ykey][0]['input'], *optdict['addlinelayer_in'])
            layer_in.setXData(times)        
            # Set the line width 
            layer_in.setLineWidth(optdict['setlinewidth_in'])        

            # Add out line layer
            layer_out = c.addAreaLayer(y_ps[ykey][0]['output'], *optdict['addlinelayer_out'])
            layer_out.setXData(times)     
            layer_out.setLineWidth(optdict['setlinewidth_out'])
            layer_out.setBorderColor(optdict['addlinelayer_out'][0])

            # Add tr line layer
            '''layer_tr = c.addLineLayer(y_ps[ykey][0]['output'], *optdict['addlinelayer_tr'])
	    layer_tr.setXData(times)        
	    # Set the line width
	    layer_tr.setLineWidth(optdict['setlinewidth_tr'])'''
            #-----------------
            retlist.append(c.makeChart2(0))

        return retlist

    def cddraw_nfs_n_traf(self, *args, **kwargs):
        if len(kwargs['servers']) == 1:
            return self.cddraw_nfs_nas_traf(*args, **kwargs)
        else:
            return self.cddraw_nfs_total_nass_traf(*args, **kwargs)

    def cddraw_nfs_nas_traf(self, *args, **kwargs):
        try:	    
            #get a string from #selstrdict# dictionary with a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', direction', '', args[0].isoformat(' '), args[1].isoformat(' '), "AND (nas_id=%d)" % kwargs['servers'][0])
        except Exception, ex:
            raise ex
        data = bpbl.get_traf(selstr, kwargs.has_key('sec') and kwargs['sec'])	
        if not data: print "Dataset is empty"; data = ([], [], [], [], '', 1)
        (times, y_in, y_out, y_tr, bstr, sec) = data 
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_nas_traf']

        retlist = []
        c = XYChart(*optdict['xychart'])

        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)

        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])

        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])

        #if optdict['outfill']:
            # Add out line layer
            #layer_out = c.addDataLayer(y_out, *optdict['addlinelayer_out'])
            #layer_out.setXData(times)     
            #layer_out.setLineWidth(optdict['setlinewidth_out'])

        # Add in line layer 
        layer_in = c.addLineLayer(y_in, *optdict['addlinelayer_in'])
        layer_in.setXData(times)        
        # Set the line width 
        layer_in.setLineWidth(optdict['setlinewidth_in'])        

        # Add out line layer
        layer_out = c.addAreaLayer(y_out, *optdict['addlinelayer_out'])
        layer_out.setXData(times)     
        layer_out.setLineWidth(optdict['setlinewidth_out'])
        layer_out.setBorderColor(optdict['addlinelayer_out'][0])

        '''# Add tr line layer
	layer_tr = c.addLineLayer(y_tr, *optdict['addlinelayer_tr'])
        layer_tr.setXData(times)        
        # Set the line width
        layer_tr.setLineWidth(optdict['setlinewidth_tr'])'''

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def cddraw_nfs_total_nass_traf(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', nas_id', '', args[0].isoformat(' '), args[1].isoformat(' '), ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']])))
        except Exception, ex:
            raise ex
        data = bpbl.get_total_users_traf(selstr, kwargs.has_key('sec') and kwargs['sec'])
        print "----------------------------"
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, y_total_n, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_nass_traf']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nas'] % ("IN (%s)" % ', '.join([str(int) for int in kwargs['servers']]))
        except Exception, ex:
            raise ex
        data = bpbl.get_nas(selstr)
        print "----------------------------"
        print data
        if not data: print "Dataset is empty"; return [] 

        for tuple in data:
            try:
                layer = c.addLineLayer(y_total_n[str(tuple[1])], -1, tuple[0].encode('utf-8'))
                layer.setXData(times)        
                # Set the line width	
                layer.setLineWidth(optdict['setlinewidth_total'])
            except Exception, ex:
                print ex     

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def cddraw_nfs_total_classes_speed(self, *args, **kwargs):
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['nfs'] % (', traffic_class_id', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                          (((kwargs.has_key('nas')) and ("AND (nas_id IN (%s))" % ', '.join([str(int) for int in kwargs['servers']]))) or  ((not kwargs.has_key('nas')) and ' ')) + \
                                          (((kwargs.has_key('trclass')) and (" AND (traffic_class_id IN (%s))" % ', '.join([str(int) for int in kwargs['trclass']]))) or  ((not kwargs.has_key('trclass')) and ' ')))
        except Exception, ex:
            raise ex
        data = bpbl.get_total_users_speed(selstr, kwargs.has_key('sec') and kwargs['sec'])
        print "----------------------------"
        print data
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, y_total_n, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['nfs_total_classes_speed']
        retlist = []
        c = XYChart(*optdict['xychart']) 
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle'])        
        # Add a title to the y axis 
        c.yAxis().setTitle(*optdict['yaxissettitle'])        
        # Set the y axis line width 
        c.yAxis().setWidth(optdict['yaxissetwidth'])        
        # Add a title to the x axis 
        c.xAxis().setTitle(*optdict['xaxissettitle'])        
        # Set the x axis line width
        c.xAxis().setWidth(optdict['xaxissetwidth'])
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+' '+bstr)
        if optdict['xaxissetlabelformat']: c.xAxis().setLabelFormat(optdict['xaxissetlabelformat'])
        try:
            #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
            selstr = selstrdict['classes'] % ("IN (%s)" % ', '.join([str(int) for int in kwargs['classes']]))
        except Exception, ex:
            raise ex
        data = bpbl.get_usernames(selstr)
        print "----------------------------"
        if not data: print "Dataset is empty"; return [] 

        for tuple in data:
            try:
                layer = c.addLineLayer(y_total_n[str(tuple[1])], -1, tuple[0].encode('utf-8'))
                layer.setXData(times)        
                # Set the line width
                print "tuple###----------------------------------"
                layer.setLineWidth(optdict['setlinewidth_total'])
            except Exception, ex:
                print ex     

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def cddraw_userstrafpie(self, *args, **kwargs):
        '''Plots pie chart of traffic values on
	@axes - axes,
	@args[0:2] - with values bounded by dates @date_start, @date_end for users @(users)
	###@args[3:4] return data values###'''
        try:
            selstr = selstrdict['userstrafpie'] % (args[0].isoformat(' '), args[1].isoformat(' '), ', '.join([str(int) for int in kwargs['users']]))	
        except Exception, ex:
            raise ex
        data = bpbl.get_pie_traf(selstr)

        if not data: print "Dataset is empty"; data = ([0], ["empty"], '')
        (x, labels, bstr) = data
        optdict = self.cdchartoptdict['userstrafpie']
        retlist = []
        c = PieChart(*optdict['piechart'])
        # Set the center of the pie  and the radius
        c.setPieSize(*optdict['setpiesize'])
        c.setLabelStyle(*optdict['setlabelstyle'])
        c.setLabelLayout(SideLayout)
        # Add a title to the pie chart
        c.addTitle(*optdict['addtitle'])	
        # Draw the pie in 3D
        c.set3D()	
        # Set the pie data and the pie labels
        labels = [label.encode('utf-8') for label in labels]
        c.setData(x, labels)	
        '''try:
	    args[3] = x
	    args[4] = labels
	except:
	    pass'''
        img = c.makeChart2(0)
        formstr = "%.2f " + bstr
        x = [formstr % numx for numx in x]
        
        #kwargs['return']['data'] = [(labels[i], x[i]) for i in range(len(x))]
        lpairs = [(labels[i], x[i]) for i in range(len(x))]
        labels = [lbl.lower() for lbl in labels]
        labels.sort()

        kwargs['return']['data'] = [(lpr[0], lpr[1]) for slbl in labels for lpr in lpairs if slbl == lpr[0].lower()]
        # Explode the 1st sector (index = 0)
        #c.setExplode(0)
        # output the chart
        retlist.append(img)	
        return retlist

    def cddraw_sessions(self, *args, **kwargs):	
        '''Plots bar chart of sessions/time on
	@axes - axes,
	@args[0:2] - for user = @account_id, with values bounded by dates @date_start, @date_end'''
        try:
            selstr = selstrdict['sessions'] % (', '.join([str(intt) for intt in kwargs['users']]), args[0].isoformat(' '), args[1].isoformat(' '), args[0].isoformat(' '), args[1].isoformat(' '))
        except Exception, ex:
            raise ex
        print "predata:"
        data = bpbl.get_sessions(selstr)
        print "postdata"
        #print data
        if not data: print "Dataset is empty"; data = ([], [], [], [], [])
        (t_start, t_end, sessid, username, protocol) = data
        kwargs['return']['data'] = [(username[i], sessid[i], t_start[i], t_end[i], protocol[i]) for i in range(len(sessid))]
        try:
            mins = min([date for date in t_start if date])
            maxe = max([date for date in t_end if date])
            for i in range(len(t_start)):
                if not t_start[i]: t_start[i] = mins
                if not t_end[i]: t_end[i] = maxe
        except Exception, ex:
            print "Session exception: ", ex
        # if username.count(username[0]) == len(username)
        ucount = defaultdict(int)
        for usr in username:
            ucount[usr] += 1
        unames = [key.lower() for key in ucount.iterkeys()]
        unames.sort()
        unames = [key for uname in unames for key in ucount.iterkeys() if key.lower() == uname]
        nindex = {}
        for i in range(len(unames)):
            nindex[unames[i]] = i
        tIndexes = []
        i = 0
        ''' for uname in unames:
            for j in range(ucount[uname]):
                tIndexes.append(i)
            i += 1
        print tIndexes'''
        for uuname in username:
            tIndexes.append(nindex[uuname])
        t_start = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in t_start]
        t_end   = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in t_end]
        #labels  = [username[i] + ' | ' + sessid[i] for i in range(len(sessid))]
        labels = unames
        startDate = chartTime(args[0].year, args[0].month, args[0].day, args[0].hour, args[0].minute, args[0].second)
        endDate   = chartTime(args[1].year, args[1].month, args[1].day, args[1].hour, args[1].minute, args[1].second)


        optdict = self.cdchartoptdict['sessions']
        #if len(labels) > 12:
        xyc = list(optdict['xychart'])
        spa = list(optdict['setplotarea'])
        if len(labels) >= 1:
            #fllen = float(len(labels))
            #mVal = fllen / 10 - ((fllen / 10)*(fllen / 100))            
            #xyc[1] = int(xyc[1]*mVal)            
            #if xyc[1] < 80:
            xyc[1] = 60 + 14*len(labels)
            spa[3] = xyc[1] - 60
            #optdict['xychart'] = xyc
            #optdict['setplotarea'] = spa
            
        retlist = []
        #c = XYChart(*optdict['xychart'])
        c = XYChart(*xyc)

        # Add a title to the chart using 15 points Times Bold Itatic font, with white
        # (ffffff) text on a deep blue (000080) background
        c.addTitle(*optdict['addtitle'])

        # Set the plotarea and size of pixels. Use alternative
        # white/grey background. Enable both horizontal and vertical grids by setting their
        # colors to grey (c0c0c0). Set vertical major grid (represents month boundaries) 2
        # pixels in width
        #c.setPlotArea(*optdict['setplotarea'])	
        c.setPlotArea(*spa)	
        # swap the x and y axes to create a horziontal box-whisker chart
        c.swapXY()	
        #----
        c.yAxis().addMark(startDate, c.dashLineColor(*optdict['dashlinecolor']))
        c.yAxis().addMark(endDate, c.dashLineColor(*optdict['dashlinecolor']))
        #----
        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        # Set multi-style axis label formatting. Month labels are in Arial Bold font in "mmm
        # d" format. Weekly labels just show the day of month and use minor tick (by using
        # '-' as first character of format string).
        #c.yAxis().setMultiFormat(StartOfMonthFilter(), "<*font=arialbd.ttf*>{value|mmm d}", StartOfDayFilter(), "-{value|d}")

        # Set the y-axis to shown on the top (right + swapXY = top)
        c.setYAxisOnRight()

        # Set the labels on the x axis
        labels = [label.encode('utf-8') for label in labels]
        c.xAxis().setLabels(labels)

        # Reverse the x-axis scale so that it points downwards.
        c.xAxis().setReverse()	
        # Set the horizontal ticks and grid lines to be between the bars
        c.xAxis().setTickOffset(optdict['settickoffset'])	
        # Add a box-whisker layer showing the box only.
        layer = c.addBoxWhiskerLayer(t_start, t_end, *optdict['addboxwhiskersess'])
        layer.setXData(tIndexes)
        #layer.setDataWidth(int(spa[3]*0.4/len(labels)))
        layer.setDataWidth(8)
        #return data

        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist


    def cddraw_trans_deb(self, *args, **kwargs):
        '''Plots bar chart of debit transactions/time on
	@axes - axes,
	@args[0:1] - for all users, with values bounded by dates @date_start, @date_end'''
        try:
            selstr = selstrdict['trans'] % ('> 0', args[0].isoformat(' '), args[1].isoformat(' '))
        except Exception, ex:
            raise ex	
        data = bpbl.get_trans(selstr, 'deb', kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, summ, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['trans_deb']
        retlist = []
        c = XYChart(*optdict['xychart'])
        # Add a title to the chart using 15 points Times Bold Itatic font, with white
        # (ffffff) text on a deep blue (000080) background	
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle']) 

        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        # Set the plotarea and size of pixels. Use alternative
        # white/grey background. Enable both horizontal and vertical grids by setting their
        # colors to grey (c0c0c0). Set vertical major grid (represents month boundaries) 2
        # pixels in width
        print summ
        #print times
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+optdict['currency'])
        #layer = c.addBarLayer(summ, *optdict['addbarlayer'])
        #c.xAxis().setLabels2(times)
        #layer.setXData(times)	
        print "-----------------------------------------"
        print len(summ)
        print sec
        c.addScatterLayer(times, summ, *optdict['addscatterlayer'])
        layer_tr = c.addLineLayer(summ, *optdict['addlinelayer_trans'])
        layer_tr.setXData(times)        
        # Set the line width 
        layer_tr.setLineWidth(optdict['setlinewidth_trans']) 
        #c.xAxis().setTickOffset(optdict['settickoffset'])	
        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def cddraw_trans_crd(self, *args, **kwargs):
        '''Plots bar chart of credit transactions/time on
	@axes - axes,
	@args[0:1] - for all users, with values bounded by dates @date_start, @date_end'''
        try:
            selstr = selstrdict['trans'] % ('< 0', args[0].isoformat(' '), args[1].isoformat(' '))
        except Exception, ex:
            raise ex	
        data = bpbl.get_trans(selstr, 'crd', kwargs.has_key('sec') and kwargs['sec'])
        if not data: print "Dataset is empty"; data = ([], [], '', 1)
        (times, summ, bstr, sec) = data
        kwargs['return']['sec'] = sec
        times = [chartTime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second) for tm in times]
        optdict = self.cdchartoptdict['trans_deb']
        retlist = []
        c = XYChart(*optdict['xychart'])
        # Add a title to the chart using 15 points Times Bold Itatic font, with white
        # (ffffff) text on a deep blue (000080) background	
        if not optdict['antialias']:
            c.setAntiAlias(0)
        c.setPlotArea(*optdict['setplotarea'])
        c.setColors(optdict['setcolors'])
        c.addLegend(*optdict['addlegend']).setBackground(optdict['legendbackground'])

        if not optdict['autoticks']:
            xplen = optdict['setplotarea'][2] - optdict['setplotarea'][0]
            yplen = optdict['setplotarea'][3] - optdict['setplotarea'][1]
            c.xAxis().setTickDensity(yplen / 5, yplen / 25)
            c.yAxis().setTickDensity(yplen / 5, yplen / 25)
        # Add a title to the chart 
        c.addTitle(*optdict['addtitle']) 

        c.xAxis().setLabelStyle(*optdict['xaxissetlabelstyle'])
        c.yAxis().setLabelStyle(*optdict['yaxissetlabelstyle'])
        # Set the plotarea and size of pixels. Use alternative
        # white/grey background. Enable both horizontal and vertical grids by setting their
        # colors to grey (c0c0c0). Set vertical major grid (represents month boundaries) 2
        # pixels in width
        print summ
        #print times
        c.yAxis().setLabelFormat(optdict['yaxissetlabelformat']+optdict['currency'])
        #layer = c.addBarLayer(summ, *optdict['addbarlayer'])
        #c.xAxis().setLabels2(times)
        #layer.setXData(times)	
        print "-----------------------------------------"
        print len(summ)
        print sec
        c.addScatterLayer(times, summ, *optdict['addscatterlayer'])
        layer_tr = c.addLineLayer(summ, *optdict['addlinelayer_trans'])
        layer_tr.setXData(times)        
        # Set the line width 
        layer_tr.setLineWidth(optdict['setlinewidth_trans']) 
        #c.xAxis().setTickOffset(optdict['settickoffset'])	
        # output the chart
        retlist.append(c.makeChart2(0))	
        return retlist

    def get_options(self, chartname):
        try:
            return self.cdchartoptdict[chartname]
        except:
            return {'errormessage': "No such chart: "+chartname}

    def set_options(self, chartname, optdict):
        for key in optdict.iterkeys():
            if self.cdchartoptdict[chartname].has_key(key): self.cdchartoptdict[chartname][key] = optdict[key]

    def translate_args(self, *args, **kwargs):
        if '' + args[0] == "nfs_u_traf":
            if len(kwargs['users']) == 1:
                mname = "nfs_user_traf"
            else:
                mname = "nfs_total_users_traf"

        elif '' + args[0] == "nfs_u_speed":
            if len(kwargs['users']) == 1:
                mname = "nfs_user_speed"
            else:
                mname = "nfs_total_users_speed"

        elif '' + args[0] == "nfs_n_traf":
            if len(kwargs['servers']) == 1:
                mname = "nfs_nas_traf"
            else:
                mname = "nfs_total_nass_traf"
        else:
            mname = args[0]

        return mname