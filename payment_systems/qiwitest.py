import urllib, urllib2
params=u"""<?xml version="1.0" encoding="utf-8"?>
<request>
<protocol-version>4.00</protocol-version>
<request-type>3</request-type>
<extra name="password">df[vehrf2007</extra>
<terminal-id>11468</terminal-id>
</request>
"""

params=u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>33</request-type>
    <extra name="password">df[vehrf2007</extra>
    <terminal-id>11468</terminal-id>
    <bills-list>
    <bill txn-id="123"/>
    </bills-list>
</request>

"""

params=u"""<?xml version="1.0" encoding="utf-8"?>
<request>
    <protocol-version>4.00</protocol-version>
    <request-type>30</request-type>
    <extra name="password">df[vehrf2007</extra>
    <terminal-id>11468</terminal-id>
    <extra name="comment"></extra>
    <extra name="to-account">1234567890</extra>
    <extra name="amount">100.00</extra>
    <extra name="txn-id">123</extra>
    <extra name="ALARM_SMS">0</extra>
    <extra name="ACCEPT_CALL">0</extra>
    <extra name="ltime">60</extra>
</request>

"""

#enc_params = urllib.quote(params)
#user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
#headers = { 'User-Agent' : user_agent }
request = urllib2.Request("http://ishop.qiwi.ru/xml",params)
#request.add_header('Content-Type', 'text/xml')
#request.add_header('Accept', 'application/xml')
response = urllib2.urlopen(request)
print response.read()


"""
<request-type>3</request-type>

<?xml version="1.0" encoding="utf-8"?>
<request>
<protocol-version>4.00</protocol-version>
<request-type>3</request-type>
<extra name="password">df[vehrf2007</extra>
<terminal-id>11468</terminal-id>
<extra name="serial">123</extra>
</request>
"""