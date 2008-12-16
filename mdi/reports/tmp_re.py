import re
import sys

# common variables

rawstr = r"""\s*(?P<port>\d+)(?P<desc>.*)"""
embedded_rawstr = r"""\s*(?P<port>\d+)(?P<desc>.*)"""
matchstr = """                  1tcpmux
                  5rje
                  7echo
                  9discard
                  11systat
                  13daytime
                  15netstat
                  17qotd
                  18send/rwp
                  19chargen
                  20ftp-data
                  21ftp
                  22ssh, pcAnywhere
                  23Telnet
                  25SMTP
                  27ETRN
                  29msg-icp
                  31msg-auth
                  33dsp
                  37time
                  38RAP
                  39rlp
                  42nameserv
                  43whois
                  49TACACS
                  50RMCP
                  53DNS
                  57MTP
                  59NFILE
                  63whois++
                  66sql*net
                  67bootps
                  68bootpd/dhcp
                  69tftp
                  70Gopher
                  79finger
                  80www-http
                  88Kerberos, WWW
                  95supdup
                  96DIXIE
                  98linuxconf
                  101HOSTNAME
                  102ISO, X.400, ITOT
                  105cso
                  106poppassd
                  109POP2
                  110POP3
                  111Sun RPC Portmapper
                  113identd/auth
                  115sftp
                  117uucp
                  119NNTP
                  120CFDP
                  123NTP
                  124SecureID
                  129PWDGEN
                  133statsrv
                  135loc-srv/epmap
                  137netbios-ns
                  138netbios-dgm (UDP)
                  139NetBIOS
                  143IMAP
                  144NewS
                  152BFTP
                  153SGMP
                  161SNMP
                  175vmnet
                  177XDMCP
                  178NextStep
                  179BGP
                  180SLmail
                  199smux
                  210Z39.50
                  218MPP
                  220IMAP3
                  259ESRO
                  264FW1_topo
                  311Apple WebAdmin
                  350MATIP type A
                  351MATIP type B
                  363RSVP tunnel
                  366ODMR)
                  387AURP
                  389LDAP
                  407Timbuktu
                  434Mobile IP
                  443ssl
                  444snpp
                  445SMB
                  458QuickTime TV/Conferencing
                  468Photuris
                  500ISAKMP, pluto
                  512biff, rexec
                  513who, rlogin
                  514syslog, rsh
                  515lp, lpr, line printer
                  517talk
                  520RIP
                  521RIPng
                  522ULS
                  531IRC
                  543KLogin, AppleShare over IP
                  545QuickTime
                  548AFP
                  554RTSP
                  555phAse Zero
                  563NNTP over SSL
                  575VEMMI
                  581BDP
                  593MS-RPC
                  608SIFT/UFT
                  626Apple ASIA
                  631IPP 
                  635mountd
                  636sldap
                  642EMSD
                  648RRP 
                  655tinc
                  660Apple MacOS Server Admin
                  666Doom
                  674ACAP
                  687AppleShare IP Registry
                  700buddyphone
                  705AgentX for SNMP
                  901swat, realsecure
                  993s-imap
                  995s-pop
                  1062Veracity
                  1080SOCKS
                  1085WebObjects
                  1227DNS2Go
                  1243SubSeven
                  1338Millennium Worm
                  1352Lotus Notes
                  1381ANLM
                  1417Timbuktu
                  1418Timbuktu
                  1419Timbuktu
                  1433MSSQL Server
                  1434MSSQL Monitor
                  1494Citrix ICA Protocol
                  1503T.120
                  1521Oracle SQL
                  1525prospero
                  1526prospero
                  1527tlisrv
                  1604Citrix ICA, MS TS
                  1645RADIUS Authentication
                  1646RADIUS Accounting
                  1680Carbon Copy
                  1701L2TP/LSF
                  1717Convoy
                  1720H.323/Q.931
                  1723PPTP control port
                  1755Windows Media .asf
                  1758TFTP multicast
                  1812RADIUS server
                  1813RADIUS accounting
                  1818ETFTP
                  1973DLSw DCAP/DRAP
                  1985HSRP
                  1999Cisco AUTH
                  2001glimpse
                  2049NFS
                  2064distributed.net
                  2065DLSw
                  2066DLSw
                  2106MZAP
                  2140DeepThroat
                  2327Netscape Conference
                  2336Apple UG Control
                  2427MGCP gateway
                  2504WLBS
                  2535MADCAP
                  2543sip
                  2592netrek
                  2727MGCP call agent
                  2628DICT
                  2998ISS RSC Service Port
                  3000Firstclass
                  3031Apple AgentVU
                  3128squid
                  3130ICP
                  3150DeepThroat
                  3264ccmail
                  3283Apple NetAssitant
                  3288COPS
                  3305ODETTE
                  3306mySQL
                  3389RDP Protocol
                  3521netrek
                  4000icq
                  4321rwhois
                  4333mSQL
                  4827HTCP
                  5004RTP
                  5005RTP
                  5010Y!M
                  5060SIP
                  5190AIM
                  5500securid
                  5501securidprop
                  5423Apple VirtualUser
                  5631PCAnywhere data
                  5632PCAnywhere
                  5800VNC
                  5801VNC
                  5900VNC
                  5901VNC
                  6000X Windows
                  6112BattleNet
                  6502Netscape Conference
                  6667IRC
                  6668IRC
                  6669IRC
                  6776Sub7
                  6970RTP
                  7007MSBD
                  7070RealServer/QuickTime
                  7778Unreal
                  7648CU-SeeMe
                  7649CU-SeeMe
                  8010WinGate 2.1
                  8080HTTP
                  8181HTTP
                  8383IMail WWW
                  8875napster
                  8888napster
                  10008cheese worm
                  11371PGP 5 Keyserver
                  13223PowWow
                  13224PowWow
                  14237Palm
                  14238Palm
                  18888LiquidAudio
                  21157Activision
                  23213PowWow
                  23214PowWow
                  23456EvilFTP
                  26000Quake
                  27001QuakeWorld
                  27010Half-Life
                  27015Half-Life
                  27960QuakeIII
                  30029AOL Admin
                  31337Back Orifice
                  32777rpc.walld
                  40193Novell
                  41524arcserve discovery
                  45000Cisco NetRanger
                  32773rpc.ttdbserverd
                  32776rpc.spray
                  32779rpc.cmsd
                  38036timestep"""

# method 1: using a compile object
compile_obj = re.compile(rawstr)
match_obj = compile_obj.search(matchstr)

# method 2: using search function (w/ external flags)
match_obj = re.search(rawstr, matchstr)

# method 3: using search function (w/ embedded flags)
match_obj = re.search(embedded_rawstr, matchstr)

# Retrieve group(s) from match_obj
all_groups = match_obj.groups()
print all_groups
# Retrieve group(s) by index
group_1 = match_obj.group(1)
group_2 = match_obj.group(2)
print group_1
# Retrieve group(s) by name
prs = compile_obj.findall(matchstr)
d2 = dict(prs)

kss = [str(num) for num in sorted([int(val) for val in d2.iterkeys()])]
lstr1 = []
#for i in range(len(kss)):
sdt = '{' + ', '.join([repr(ks)+": "+repr(d2[ks]) for ks in kss]) + '}'
print sdt    
f = open("dict7", 'wb')
f. write(sdt)