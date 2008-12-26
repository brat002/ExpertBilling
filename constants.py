rules={
       
        'allow_pptp':u"""/ppp profile add name=internet only-one=yes use-compression=no use-encryption=yes use-vj-compression=yes local-address=%s;/interface pptp-server server set enabled=yes authentication=%s default-profile=internet;
        """,
        'allow_radius':u"""
        /ppp aaa set accounting=yes use-radius=yes interim-update=%s; /radius add address=%s disabled=no secret=%s timeout=3000;""",
        'smtp_protect' : u"""
        /ip firewall filter

add chain=forward protocol=tcp dst-port=25 src-address-list=spammer
action=drop comment="BLOCK SPAMMERS OR INFECTED USERS"

add chain=forward protocol=tcp dst-port=25 connection-limit=30,32 limit=50,5 action=add-src-to-address-list
address-list=spammer address-list-timeout=30m comment="Detect and add-list SMTP virus or spammers"

/system script
add name="spammers" source=":log error \"----------Users detected like \
    SPAMMERS -------------\";
\n:foreach i in \[/ip firewall address-list find \
    list=spammer\] do={:set usser \[/ip firewall address-list get \$i \
    address\];
\n:foreach j in=\[/ip hotspot active find address=\$usser\] \
    do={:set ip \[/ip hotspot active get \$j user\];
\n:log error \$ip;
\n:log \
    error \$usser} };" policy=ftp,read,write,policy,test,winbox  """,
    
    "malicious_trafic":"""
    
    /ip firewall filter
add chain=forward connection-state=established comment="allow established connections"  
add chain=forward connection-state=related comment="allow related connections"
add chain=forward connection-state=invalid action=drop comment="drop invalid connections"  

add chain=virus protocol=tcp dst-port=135-139 action=drop comment="Drop Blaster Worm" 
add chain=virus protocol=udp dst-port=135-139 action=drop comment="Drop Messenger Worm"    
add chain=virus protocol=tcp dst-port=445 action=drop comment="Drop Blaster Worm" 
add chain=virus protocol=udp dst-port=445 action=drop comment="Drop Blaster Worm" 
add chain=virus protocol=tcp dst-port=593 action=drop comment="________" 
add chain=virus protocol=tcp dst-port=1024-1030 action=drop comment="________" 
add chain=virus protocol=tcp dst-port=1080 action=drop comment="Drop MyDoom" 
add chain=virus protocol=tcp dst-port=1214 action=drop comment="________" 
add chain=virus protocol=tcp dst-port=1363 action=drop comment="ndm requester" 
add chain=virus protocol=tcp dst-port=1364 action=drop comment="ndm server" 
add chain=virus protocol=tcp dst-port=1368 action=drop comment="screen cast" 
add chain=virus protocol=tcp dst-port=1373 action=drop comment="hromgrafx" 
add chain=virus protocol=tcp dst-port=1377 action=drop comment="cichlid" 
add chain=virus protocol=tcp dst-port=1433-1434 action=drop comment="Worm" 
add chain=virus protocol=tcp dst-port=2745 action=drop comment="Bagle Virus" 
add chain=virus protocol=tcp dst-port=2283 action=drop comment="Drop Dumaru.Y" 
add chain=virus protocol=tcp dst-port=2535 action=drop comment="Drop Beagle" 
add chain=virus protocol=tcp dst-port=2745 action=drop comment="Drop Beagle.C-K" 
add chain=virus protocol=tcp dst-port=3127-3128 action=drop comment="Drop MyDoom" 
add chain=virus protocol=tcp dst-port=3410 action=drop comment="Drop Backdoor OptixPro"
add chain=virus protocol=tcp dst-port=4444 action=drop comment="Worm" 
add chain=virus protocol=udp dst-port=4444 action=drop comment="Worm" 
add chain=virus protocol=tcp dst-port=5554 action=drop comment="Drop Sasser" 
add chain=virus protocol=tcp dst-port=8866 action=drop comment="Drop Beagle.B" 
add chain=virus protocol=tcp dst-port=9898 action=drop comment="Drop Dabber.A-B" 
add chain=virus protocol=tcp dst-port=10080 action=drop comment="Drop MyDoom.B" 
add chain=virus protocol=tcp dst-port=12345 action=drop comment="Drop NetBus" 
add chain=virus protocol=tcp dst-port=17300 action=drop comment="Drop Kuang2" 
add chain=virus protocol=tcp dst-port=27374 action=drop comment="Drop SubSeven" 
add chain=virus protocol=tcp dst-port=65506 action=drop comment="Drop PhatBot, Agobot, Gaobot"
add chain=forward action=jump jump-target=virus comment="jump to the virus chain"
add chain=forward action=accept protocol=tcp dst-port=80 comment="Allow HTTP" 
add chain=forward action=accept protocol=tcp dst-port=25 comment="Allow SMTP" 
add chain=forward protocol=tcp comment="allow TCP"
add chain=forward protocol=icmp comment="allow ping"
add chain=forward protocol=udp comment="allow udp"
add chain=forward action=drop comment="drop everything else"

 """,
    'gateway':u"""
    /ip firewall nat add chain=srcnat src-address=0.0.0.0/0 action=masquerade
    """
        
       }


   
