#-*-encoding:utf-8-*-
#from bpmplQImage import bpmplQImage as bpQImage
from bpcdQImage import bpcdQImage as bpQImage
from PyQt4 import QtCore, QtGui
from xml.sax.handler import ContentHandler
from xml.sax import parse
from bpcdQImage import bpcdQImage as bpQImage
#from bpplotadapter import bpplotAdapter

import time

dssdict = {"get_accounts" : "SELECT id, username, vpn_ip_address, ipn_ip_address, ballance FROM billservice_account WHERE (id %s) ORDER BY username;", \
           "get_tarifs"   : '''SELECT account_id, 
                             ARRAY(SELECT (name || ' | ' || to_char(datetime, 'DD.MM.YYYY HH24:MI:SS')) FROM billservice_accounttarif AS subbatf, billservice_tariff as subbst   
                             WHERE (subbatf.tarif_id = subbst.id) AND (subbatf.account_id = batf.account_id) 
                             AND ((subbatf.datetime = (select max(subsubbatf.datetime) from billservice_accounttarif AS subsubbatf 
                             WHERE (subsubbatf.account_id = subbatf.account_id) 
                             AND (subsubbatf.datetime < '%s'))) 
                             OR ((subbatf.datetime BETWEEN '%s' AND '%s') )) ORDER BY datetime)  
                             AS data FROM billservice_accounttarif AS batf 
                             GROUP BY account_id HAVING (account_id NOTNULL) %s;''', \
	   "get_nas"      : "SELECT name, type, ipaddress FROM nas_nas WHERE (id IN (%s)) ORDER BY name;", \
	   "get_usernames": "SELECT username, id FROM billservice_account WHERE (id %s) ORDER BY username;", \
           "get_classes"  : "SELECT name, weight FROM nas_trafficclass WHERE (id IN (%s)) ORDER BY name;"}


borderstyles = [QtGui.QTextFrameFormat.BorderStyle_None, QtGui.QTextFrameFormat.BorderStyle_Dotted, QtGui.QTextFrameFormat.BorderStyle_Dashed, QtGui.QTextFrameFormat.BorderStyle_Solid, QtGui.QTextFrameFormat.BorderStyle_Double, QtGui.QTextFrameFormat.BorderStyle_DotDash, QtGui.QTextFrameFormat.BorderStyle_DotDotDash, QtGui.QTextFrameFormat.BorderStyle_Groove, QtGui.QTextFrameFormat.BorderStyle_Ridge, QtGui.QTextFrameFormat.BorderStyle_Inset, QtGui.QTextFrameFormat.BorderStyle_Outset]
positions    = [QtGui.QTextFrameFormat.InFlow, QtGui.QTextFrameFormat.FloatLeft, QtGui.QTextFrameFormat.FloatRight]
alignments   = [[QtCore.Qt.AlignLeft, QtCore.Qt.AlignRight, QtCore.Qt.AlignHCenter, QtCore.Qt.AlignJustify], [QtCore.Qt.AlignTop, QtCore.Qt.AlignBottom, QtCore.Qt.AlignVCenter]]

class bpReportEdit(object):
    
    
    def createreport(self, datafile, rargs, rkwargs, connection):
        editor = QtGui.QTextEdit()
        parse(datafile, reportConstructor(editor, rargs, rkwargs, connection=connection))
        return editor
    
    
class Dispatcher(object):

    def dispatch(self, prefix, name, attrs=None):
        mname = prefix + name.capitalize()
        dname = 'default' + prefix.capitalize()
        method = getattr(self, mname, None)
	print name
        if callable(method): args = ()
        else:
            method = getattr(self, dname, None)
            args = name,
        if prefix == 'start': args += attrs,
        if callable(method): method(*args)

    def startElement(self, name, attrs):
        self.dispatch('start', name, attrs)
	#print "start_" + name

    def endElement(self, name):
        self.dispatch('end', name)
	#print "end_" + name

class reportConstructor(Dispatcher, ContentHandler):

    passthrough = False

    def __init__(self, editor, rargs, rkwargs, **kwargs):
        self.editor = editor
	self.connection = None
	if kwargs.has_key('connection'):
	    self.connection = kwargs['connection']
        self.cursor = self.editor.textCursor()
        if 0:
            assert isinstance(self.cursor, QtGui.QTextCursor)
        self.chargs  = rargs
	self.chkwargs = rkwargs
	self.chcount = 0
        self.objdict = {}
        self.objdict['curchart'] = {}
	self.objdict['curtable'] = {}
	self.dateDelim = "."
	self.strftimeFormat = "%d" + self.dateDelim + "%m" + self.dateDelim + "%Y %H:%M:%S"
        self.objdict['data'] = {}
	self.objdict['frames'] = {}
	self.objdict['format'] = {}
	self.objdict['textformat'] = {}
	self.objdict['blockformat'] = {}
	self.objdict['textformat']['deftf']  = self.cursor.charFormat()
	self.objdict['blockformat']['defbf'] = self.cursor.blockFormat()
	self.objdict['tableformat'] = {}
	self.curdata  = self.objdict['data']
	self.curtable = 0
	self.isOptions = False
	self.isData = ''
	self.drawer = bpQImage(self.connection)
	self.objdict['data']['args'] = self.chargs[0]
	self.objdict['data']['chkwargs'] = self.chkwargs[0]
	self.gq = getData(self.connection)
	
        
    def startReport(self, attrs):
        self.cursor.movePosition(QtGui.QTextCursor.Start)
    
    def startFrame(self, attrs):
	if attrs.has_key('datasource'):
	    self.curdata = self.objdict['data'][attrs['datasource']]	
	print attrs['name']
        if attrs['format'] == 'currentnew':
            tmpframe  = self.cursor.currentFrame()
            tmpformat = tmpframe.frameFormat()
            self.getframeformat(attrs, tmpformat)
	    tmpframe.setFrameFormat(tmpformat)
            self.objdict['frames'][attrs['name']] = tmpframe
            self.objdict['format'][attrs['fname']] = tmpformat
        elif attrs['format'] == 'new':
            tmpformat = QtGui.QTextFrameFormat()
	    self.getframeformat(attrs, tmpformat)            
            self.objdict['frames'][attrs['name']] = self.cursor.insertFrame(tmpformat)
            self.objdict['format'][attrs['fname']] = tmpformat
	elif attrs['format'] == 'current':
	    #tmpframe  = self.cursor.currentFrame()
            tmpformat = self.cursor.currentFrame().frameFormat()
	    self.getframeformat(attrs, tmpformat)
	    self.objdict['frames'][attrs['name']] = self.cursor.insertFrame(tmpformat)
	elif attrs['format'] == 'existing':
	    try: self.objdict['frames'][attrs['name']] = self.cursor.insertFrame(self.objdict['format'][attrs['fname']])
	    except: pass
	elif attrs['format'] == 'existingnew':
	    try:
		tmpframe = self.objdict['format'][attrs['fname']]
		self.getframeformat(attrs, tmpformat)		
		self.objdict['frames'][attrs['name']] = self.cursor.insertFrame(self.objdict['format'][attrs['fname']])		
		self.objdict['format'][attrs['fname']+'_'+attrs['name']] = tmpformat
	    except: pass
        else: 
            pass
        
    def getframeformat(self, attrs, tmpformat):
	if 0:
            assert isinstance(tmpformat, QtGui.QTextFrameFormat)
	if attrs.has_key('setPadding'):
	    tmpformat.setPadding(float(attrs['setPadding']))
	if attrs.has_key('setHeight'):
	    tmpformat.setHeight(float(attrs['setHeight']))
	if attrs.has_key('setWidth'):
	    if attrs['setWidth'][-1] == '%':
		tmpformat.setWidth(QtGui.QTextLength(QtGui.QTextLength.PercentageLength, int(attrs['setWidth'][:-1])))
	    else:
		tmpformat.setWidth(float(attrs['setWidth']))
	if attrs.has_key('setMargin'):
	    tmpformat.setMargin(float(attrs['setMargin']))
	if attrs.has_key('setBorder'):
	    tmpformat.setBorder(float(attrs['setBorder']))
	if attrs.has_key('setBorderStyle'):
	    tmpformat.setBorderStyle(borderstyles[int(attrs['setBorderStyle'])])
	if attrs.has_key('setPosition'):
	    tmpformat.setPosition(positions[int(attrs['setPosition'])])
	if attrs.has_key('setBackground'):
	    tmpformat.setBackground(QtGui.QBrush(QtGui.QColor(attrs['setBackground'])))
	
    def endFrame(self):
        try:            
            self.cursor.setPosition(self.cursor.currentFrame().parentFrame().lastPosition())
        except:
            pass
        
    
    def startTextformat(self, attrs):
	textFormat = QtGui.QTextCharFormat()
	if attrs.has_key('setFontPointSize'):
	    textFormat.setFontPointSize(float(attrs['setFontPointSize']))
	if attrs.has_key('setFontWeight'):
	    textFormat.setFontWeight(float(attrs['setFontWeight']))
	if attrs.has_key('setFontUnderline'):
	    if attrs['setFontUnderline'].lower() == 'true':
		textFormat.setFontUnderline(True)
	    else: textFormat.setFontUnderline(False)
	if attrs.has_key('setFontItalic'):
	    if attrs['setFontItalic'].lower() == 'true':
		textFormat.setFontItalic(True)
	    else: textFormat.setFontItalic(False)
	if attrs.has_key('setFontFamily'):
	    textFormat.setFontFamily(attrs['setFontFamily'])
	if attrs.has_key('setForeground'):
	    textFormat.setForeground(QtGui.QBrush(QtGui.QColor(attrs['setForeground'])))
	if attrs.has_key('setBackground'):
	    textFormat.setBackground(QtGui.QBrush(QtGui.QColor(attrs['setBackground'])))
	
	self.objdict['textformat'][attrs['name']] = textFormat
	
    def startBlockformat(self, attrs):
	blockFormat = QtGui.QTextBlockFormat()
	if attrs.has_key('setAlignment'):
	    if len(attrs['setAlignment']) == 2:
		blockFormat.setAlignment(alignments[0][int(attrs['setAlignment'][1])] | alignments[1][int(attrs['setAlignment'][0])])
	self.objdict['blockformat'][attrs['name']] = blockFormat
	
    def startFrameformat(self, attrs):
	if attrs['format'] == 'currentnew':
            tmpframe  = self.cursor.currentFrame()
            tmpformat = tmpframe.frameFormat()
            self.getframeformat(attrs, tmpformat)
	    tmpframe.setFrameFormat(tmpformat)
            self.objdict['format'][attrs['fname']] = tmpformat
        elif attrs['format'] == 'new':
            tmpformat = QtGui.QTextFrameFormat()
	    self.getframeformat(attrs, tmpformat)            
            self.cursor.currentFrame().setFrameFormat(tmpformat)
            self.objdict['format'][attrs['fname']] = tmpformat
	elif attrs['format'] == 'parent':
	    #tmpframe  = self.cursor.currentFrame()#
	    try:
		tmpformat = self.cursor.currentFrame().parentFrame().frameFormat()
		self.getframeformat(attrs, tmpformat)
		self.cursor.currentFrame().setFrameFormat(tmpformat)
		self.objdict['format'][attrs['fname']] = tmpformat
	    except: pass
	elif attrs['format'] == 'existing':
	    try: self.cursor.currentFrame().setFrameFormat(self.objdict['format'][attrs['fname']])
	    except: pass
	elif attrs['format'] == 'existingnew':
	    try:
		tmpframe = self.objdict['format'][attrs['fname']]
		self.getframeformat(attrs, tmpformat)
		self.cursor.currentFrame().setFrameFormat(self.objdict['format'][attrs['fname']])		
		self.objdict['format'][attrs['fname']+'_'+attrs['name']] = tmpformat
	    except: pass
        else: 
            pass
	
    def startInserttext(self, attrs):
	try:    self.cursor.insertText(attrs['text'], self.objdict['textformat'][attrs['textformat']])
	except: self.cursor.insertText(attrs['text'])
	
    def startInsertnontext(self, attrs):
        try:    self.cursor.insertText(str(attrs['text']), self.objdict['textformat'][attrs['textformat']])
	except: self.cursor.insertText(str(attrs['text']))
	
    def startInsertdatatext(self, attrs):
	text = self.getdatatext(attrs)
	if text:
	    try:    self.cursor.insertText(text, self.objdict['textformat'][attrs['textformat']])
	    except: self.cursor.insertText(text)
	    
    def startInsertdatanontext(self, attrs):
	text = self.getdatatext(attrs)
	if text:
	    if attrs.has_key('type'):
		if attrs["type"] == "date":
		    try:    self.cursor.insertText(text.strftime(self.strftimeFormat), self.objdict['textformat'][attrs['textformat']])
		    except: self.cursor.insertText(text.strftime(self.strftimeFormat))
	    else:
		try:    self.cursor.insertText(str(text), self.objdict['textformat'][attrs['textformat']])
		except: self.cursor.insertText(str(text))
        

    
	
    def startInsertblock(self, attrs):
        #self.cursor.insertBlock()
        try:    self.cursor.insertBlock(self.objdict['blockformat'][attrs['blockformat']])
	except: self.cursor.insertBlock()

    def startChart(self, attrs):
	print attrs['name']
        cname = attrs['name']
        
        self.objdict['curchart']['type'] = attrs['type']
	if not self.chkwargs[self.chcount].has_key('return'):
	    self.chkwargs[self.chcount]['return'] = {}
	#kwargs = {'return':{}}
	#rargs = self.chargs[self.chcount]
	if self.chkwargs[self.chcount].has_key('options'):
	    self.drawer.set_options(attrs['type'], self.chkwargs[self.chcount]['options'])
	    
        qimgs = self.drawer.bpdraw(attrs['type'], *self.chargs[self.chcount], **self.chkwargs[self.chcount])
	#print kwargs['return']['sec']
	print self.chkwargs[self.chcount]
	try   : self.objdict['data'][attrs['name'] + "_return"] = self.chkwargs[self.chcount]['return']['data']
	except Exception, ex: 
	    self.objdict['data'][attrs['name'] + "_return"] = None
	    print "<chart> exception: " + str(ex) 
	
	i = 0
	for qimg in qimgs:	    
	    tdoc = self.editor.document()
	    tdoc.addResource(QtGui.QTextDocument.ImageResource, QtCore.QUrl(cname + str(i)), QtCore.QVariant(qimg))
	    self.cursor.insertImage(cname + str(i))
	    i += 1
	if i == 0: self.cursor.insertText("Query is empty or database error!")
	    
    def endChart(self):
	self.chcount += 1
	try: 
	    self.objdict['data']['args'] = self.chargs[self.chcount]
	    self.objdict['data']['kwargs'] = self.chkwargs[self.chcount]
	except: pass

    def startGetdata(self, attrs):
        pass
    
    def startSelstring(self, attrs):
	
        data = self.gq.getdata(self.objdict['curchart']['type'], attrs['name'], *self.chargs[self.chcount], **self.chkwargs[self.chcount])
	#---------remove
	try:
	    if attrs['type'] == 'row':
		data = data[0]
	except: pass
	#---------remove
	#print data
	self.objdict['data'][attrs['dataid']] = data
	
    def getTableFormat(self, attrs, tformat):
	self.getframeformat(attrs, tformat)
	if attrs.has_key('setCellPadding'):
	    tformat.setCellPadding(float(attrs['setCellPadding']))
	if attrs.has_key('setCellSpacing'):
	    tformat.setCellSpacing(float(attrs['setCellSpacing']))
	if attrs.has_key('setAlignment'):
	    if len(attrs['setAlignment']) == 2:
		tformat.setAlignment(alignments[0][int(attrs['setAlignment'][1])] | alignments[1][int(attrs['setAlignment'][0])])
	if attrs.has_key('colConstrType'):
	    try:
		if attrs['colConstrType'] == "percentage":
		    ctype = QtGui.QTextLength.PercentageLength
		elif attrs['colConstrType'] == "variable":
		    ctype = QtGui.QTextLength.VariableLength
		elif attrs['colConstrType'] == "fixed":
		    ctype = QtGui.QTextLength.FixedLength
		else: 
		    raise Exception("No such column constraint type: " + attrs['colConstrType'])
		tformat.setColumnWidthConstraints([QtGui.QTextLength(ctype, int(constr)) for constr in attrs['colConstraints'].split(", ")])
		#------------------------------todo
	    except Exception, ex:
		print ex
    def startTable(self, attrs):
	self.objdict['curtable']  = {}
	self.objdict['curtable']['formats']   = {}
	self.objdict['curtable']['colnametf'] = self.objdict['textformat']['deftf']
	self.objdict['curtable']['celltf']    = self.objdict['textformat']['deftf']
	self.objdict['curtable']['arheadtf']  = self.objdict['textformat']['deftf']
	if attrs.has_key('colnametf'):
	    self.objdict['curtable']['colnametf'] = self.objdict['textformat'][attrs['colnametf']]
	if attrs.has_key('celltf'):
	    self.objdict['curtable']['celltf']    = self.objdict['textformat'][attrs['celltf']]
	if attrs.has_key('arheadtf'):
	    self.objdict['curtable']['arheadtf']  = self.objdict['textformat'][attrs['arheadtf']]
	if attrs.has_key('arheadbf'):
	    self.objdict['curtable']['arheadbf']  = self.objdict['blockformat'][attrs['arheadbf']]
	if attrs.has_key('datasource'):
	    self.curdata = self.objdict['data'][attrs['datasource']]
	    if not self.curdata:
		return 1
	    
	    
	if attrs['ftype'] == 'new':
	    tformat =  QtGui.QTextTableFormat()
	    self.getTableFormat(attrs, tformat)
	    self.objdict['tableformat'][attrs['fname']] = tformat
	    self.objdict['curtable']['format'] = tformat
	    self.objdict['curtable']['colnum'] = int(attrs['columns'])
	    self.objdict['curtable']['type'] = attrs['type']
	    if attrs.has_key('arheader'):
		self.objdict['curtable']['arheader'] = attrs['arheader']
	    self.objdict['curtable']['colcount'] = 0
	    self.objdict['curtable']['coltypes'] = []
	    self.objdict['curtable']['colnames'] = []
	elif attrs['ftype'] == 'existing':
	    self.objdict['curtable']['format'] = self.objdict['tableformat'][attrs['fname']]
	    self.objdict['curtable']['colnum'] = int(attrs['columns'])
	    self.objdict['curtable']['type'] = attrs['type']
	    if attrs.has_key('arheader'):
		self.objdict['curtable']['arheader'] = attrs['arheader']
	    self.objdict['curtable']['colcount'] = 0
	    self.objdict['curtable']['coltypes'] = []
	    self.objdict['curtable']['colnames'] = []
	else:
	    pass
	
    def startColumn(self, attrs):
	#self.cursor = self.curtable.cellAt(0, self.objdict['curtable']['colcount']).firstCursorPosition()
	#self.cursor.insertText(attrs['name'])
	self.objdict['curtable']['colcount'] += 1
	self.objdict['curtable']['coltypes'].append(attrs['type'])
	self.objdict['curtable']['colnames'].append(attrs['name'])
	
	if (attrs['type'] == 'table') and attrs.has_key('tftype'):
	    if attrs['tftype'] == 'new':
		tformat =  QtGui.QTextTableFormat()
		self.getTableFormat(attrs, tformat)
		#tformat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 70), QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 30)])
		self.objdict['tableformat'][attrs['tfname']] = tformat
		self.objdict['curtable']['formats'][str(self.objdict['curtable']['colcount'] - 1)] = tformat
	    else:
		self.objdict['curtable']['formats'][str(self.objdict['curtable']['colcount'] - 1)] = self.objdict['tableformat'][attrs['tfname']]
	if (attrs['type'] == 'table') or (attrs['type'] == 'lines'):
	    mergedata = self.objdict['data'][attrs['datasource']]
	    if not (self.curdata and mergedata):
		print "One of datasources is empty!"
		return 1
	    ibase  = int(attrs['ibase'])
	    #imerge = int(attrs['imerge'])
	    self.curdata = [list(tuple) for tuple in self.curdata]
	    print len(mergedata)
	    '''for m_el in mergedata:
		i = 0
		for c_el in self.curdata:
		    if m_el[0] == c_el[ibase]:
			break
		    i +=1
		if i >= len(self.curdata): 
		    #self.curdata[i].insert(self.objdict['curtable']['colcount'] - 1, m_el[1])
		    continue
		print i
		print m_el
		self.curdata[i].insert(self.objdict['curtable']['colcount'] - 1, m_el[1])'''
	    dummy = ['']
	    for j in range(1, len(mergedata)):
		#dummy.append(['  |  '])
		dummy.append([])
	    print "##########################"
	    #print dummy
	    for i in range(len(self.curdata)):
		j = 0
		for m_el in mergedata:
		    if m_el[0] == self.curdata[i][ibase]:
			self.curdata[i].insert(self.objdict['curtable']['colcount'] - 1, *m_el[1:])
			print m_el
			print m_el[1:]
			break
		    j += 1
		if j >= len(mergedata):
		    try:
			self.curdata[i].insert(self.objdict['curtable']['colcount'] - 1, dummy[1])
			print repr(dummy[1])
		    except:
			self.curdata[i].insert(self.objdict['curtable']['colcount'] - 1, [])
		
		
	    
	
	
    def endTable(self):	
	if self.objdict['curtable']['colcount'] != self.objdict['curtable']['colnum']:
	    raise Exception("Wrong column number!")
	colnametf = self.objdict['curtable']['colnametf']
	celltf    = self.objdict['curtable']['celltf']
	arheadtf  = self.objdict['curtable']['arheadtf']
	if self.objdict['curtable']['type'] == 'normal':
	    if not self.curdata:
		print "Dataset is empty!"
		return 1
	    
	    try:    self.cursor.insertBlock(self.objdict['curtable']['arheadbf'])
	    except: self.cursor.insertBlock()
	    try:
		self.cursor.insertText(self.objdict['curtable']['arheader'], arheadtf)
		self.cursor.insertBlock()
	    except: pass
	    table = self.cursor.insertTable(1, self.objdict['curtable']['colnum'], self.objdict['curtable']['format'])
	    #self.objdict['curtable']['table'] = table
	    #self.curtable = table
	    for colcnt in range(self.objdict['curtable']['colcount']):
		self.cursor = table.cellAt(0, colcnt).firstCursorPosition()
		self.cursor.insertText(self.objdict['curtable']['colnames'][colcnt], colnametf)
	    for rowdata in self.curdata:
		row = table.rows()
		table.insertRows(row, 1)
		for colcnt in range(self.objdict['curtable']['colcount']):
		    self.cursor = table.cellAt(row, colcnt).firstCursorPosition()
		    if self.objdict['curtable']['coltypes'][colcnt] == 'string':
			self.cursor.insertText(rowdata[colcnt], celltf)
		    elif self.objdict['curtable']['coltypes'][colcnt] == 'date':
			self.cursor.insertText(rowdata[colcnt].strftime(self.strftimeFormat), celltf)
		    elif self.objdict['curtable']['coltypes'][colcnt] == 'table':
			print rowdata[colcnt]
			if not rowdata[colcnt]:
			    continue
			stcols = len(rowdata[colcnt][0].split(' | '))
			strows = len(rowdata[colcnt])
			curpos = self.cursor.position()
			print strows, stcols
			if self.objdict['curtable']['formats'].has_key(str(colcnt)):
			    subtable = self.cursor.insertTable(strows, stcols, self.objdict['curtable']['formats'][str(colcnt)])
			else:
			    subtable = self.cursor.insertTable(strows, stcols)
			for i in range(strows):
			    strow = rowdata[colcnt][i].split(' | ')
			    print strow
			    j = 0
			    for val in strow:
				print i,j, val
				self.cursor = subtable.cellAt(i, j).firstCursorPosition()
				self.cursor.insertText(QtCore.QString.fromUtf8(val), celltf)
				j += 1
			self.cursor.setPosition(curpos)
		    elif self.objdict['curtable']['coltypes'][colcnt] == 'lines':
			print rowdata[colcnt]
			for val in rowdata[colcnt]:
			    self.cursor.insertText(QtCore.QString.fromUtf8(val), celltf)
			    self.cursor.insertBlock()
			self.cursor.deletePreviousChar()
		    else:
			self.cursor.insertText(str(rowdata[colcnt]), celltf)
			
	elif self.objdict['curtable']['type'] == 'array':
	    if not self.curdata:
		print "Dataset is empty!"
		return 1
	    for tbl in range(len(self.curdata)):
		self.cursor.insertBlock()
		try:    self.cursor.insertBlock(self.objdict['curtable']['arheadbf'])
		except: self.cursor.insertBlock()
		self.cursor.insertBlock()
		self.cursor.insertText(self.objdict['curtable']['arheader'] % self.curdata[tbl][0], arheadtf)
		self.cursor.insertBlock()
		table = self.cursor.insertTable(1, self.objdict['curtable']['colnum'], self.objdict['curtable']['format'])
		#self.objdict['curtable']['table'] = table
		#self.curtable = table
		#self.cursor.insertBlock(self.objdict['curtable']['arheadbf'])
		for colcnt in range(self.objdict['curtable']['colcount']):
		    self.cursor = table.cellAt(0, colcnt).firstCursorPosition()		    
		    self.cursor.insertText(self.objdict['curtable']['colnames'][colcnt], colnametf)
		for liststr in self.curdata[tbl][1]:
		    rowdata = liststr.split(' | ')
		    row = table.rows()
		    table.insertRows(row, 1)
		    for colcnt in range(self.objdict['curtable']['colcount']):
			self.cursor = table.cellAt(row, colcnt).firstCursorPosition()
			self.cursor.insertText(QtCore.QString.fromUtf8(rowdata[colcnt]), celltf)
			'''if self.objdict['curtable']['coltypes'][colcnt] == 'string':
			    self.cursor.insertText(rowdata[colcnt])
			else:
			    self.cursor.insertText(str(rowdata[colcnt]))'''
		#move cursor to the parent frame	
		self.cursor.setPosition(self.cursor.currentFrame().parentFrame().lastPosition())		
	#move cursor to the last position in the frame
        self.cursor.setPosition(self.cursor.currentFrame().lastPosition())
	
	
	
    def startOptions(self, attrs):
	self.isOptions = True
	
    def endOptions(self):
	self.isOptions = False
	
    def startData(self, attrs):
	self.isData = attrs['dataid']
	
    def endData(self):
	self.isData = ''
	
    def startMovecursor(self, attrs):
	frame = 0
	try:
	    if   attrs['type'] == 'current':
		frame = self.cursor.currentFrame()
	    elif attrs['type'] == 'parent':
		frame = self.cursor.currentFrame().parentFrame()
	    elif attrs['type'] == 'existing':
		frame = self.optdict['frames'][attrs['framename']]
	except Exception, ex:
	    raise ex
	    
	if frame:
	    if attrs['position'] == 'first':
		self.cursor.movePosition(frame.firstPosition)
	    else:
		self.cursor.movePosition(frame.lastPosition)	
	

    def characters(self, chars):
        if (chars[0] == '(') or (chars[0] == '[') or (chars[0] == '{'):
	    chars = ','.join(chars.split(';'))
	    if isOptions:
		try:
		    data = {}
		    exstring = "data = " + chars
		    exec exstring
		    self.drawer.set_options(self.objdict['curchart']['type'], data)
		except Exception, ex:
		    raise ex
	    elif isData:
		try:
		    data = {}
		    exstring = "data = " + chars
		    exec exstring
		    self.objdict['data'][attrs['dataid']] = data
		except Exception, ex:
		    raise ex
	    else: 
		print("ERROR: data OR options - wrong format")
		

    def defaultStart(self, name, attrs):
        pass

    def defaultEnd(self, name):
        pass
    
    def getdatatext(self, attrs):
	text = ''
	if not self.curdata:
		print "Dataset is empty!"
		return text
	if attrs.has_key('dict'):
	    try: text = self.curdata[attrs['dict']][attrs['key']]
	    except: pass
	elif attrs.has_key('key'):
	    try: text = self.curdata[attrs['key']]
	    except: pass
	elif attrs.has_key('subindex'):
	    try: text = self.curdata[int(attrs['index'])][int(attrs['subindex'])]
	    except: pass
	else:
	    try: text = self.curdata[int(attrs['index'])]
	    except: pass
	return text
    
class getData(object):
    def __init__(self, connection):
	self.connection = connection
    def getdata(self, chtype, queryname, *args, **kwargs):
	method = getattr(self, "getdata_" + chtype, None)
	if callable(method):
	    return method(queryname, *args, **kwargs)
	else:
	    raise Exception("Method #" + chtype + "# does not exist in class getData!" )
    
    def getdata_nfs_u_traf(self, queryname, *args, **kwargs):
	if len(kwargs['users']) == 1:
	    return self.getdata_nfs_user_traf(queryname, *args, **kwargs)
	else:
	    return self.getdata_nfs_total_users_traf(queryname, *args, **kwargs)
	
    def getdata_nfs_n_traf(self, queryname, *args, **kwargs):
	if len(kwargs['servers']) == 1:
	    return self.getdata_nfs_nas_traf(queryname, *args, **kwargs)
	else:
	    return self.getdata_nfs_total_nass_traf(queryname, *args, **kwargs)

	
    def getdata_nfs_user_traf(self, queryname, *args, **kwargs):
	if queryname == 'get_accounts':
	    selstr = dssdict[queryname] % '= %d' % kwargs['users'][0]
	    data   = self.connection.get_list(selstr)
	    return data
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_classes':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['classes']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_tarifs':
	    selstr = dssdict[queryname] % (args[0].isoformat(' '), args[0].isoformat(' '), args[1].isoformat(' '), "AND (account_id = %s)" % str(kwargs['users'][0]) )
	    data   = self.connection.get_list(selstr)
	    data   = [list(tuple) for tuple in data]
	    selstr = dssdict["get_usernames"] % '= %d' % kwargs['users'][0]
	    users  = self.connection.get_list(selstr)
	    if not data: data = [['', []]]
	    for user in users:
		data[0][0] = user[0]
	    return data
	return None
	
    def getdata_nfs_user_speed(self, queryname, *args, **kwargs):
	if queryname == 'get_accounts':
	    selstr = dssdict[queryname] % '= %d' % kwargs['users'][0]
	    data   = self.connection.get_list(selstr)
	    return data
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_classes':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['classes']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_tarifs':
	    selstr = dssdict[queryname] % (args[0].isoformat(' '), args[0].isoformat(' '), args[1].isoformat(' '), "AND (account_id = %s)" % str(kwargs['users'][0]) )
	    data   = self.connection.get_list(selstr)
	    data   = [list(tuple) for tuple in data]
	    selstr = dssdict["get_usernames"] % '= %d' % kwargs['users'][0]
	    users   = self.connection.get_list(selstr)
	    if not data: data = [['', []]]
	    for user in users:
		data[0][0] = user[0]
	    return data
	return None
	
    def getdata_nfs_total_traf(self,  queryname, *args, **kwargs):
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_classes':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['classes']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	return None
		
    def getdata_nfs_total_speed(self, queryname, *args, **kwargs):
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_classes':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['classes']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	return None
  	
    def getdata_nfs_total_traf_bydir(self,  queryname, *args, **kwargs):
	    if queryname == 'get_nas':
		try:
		    selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['servers']])
		    data   = self.connection.get_list(selstr)
		    return data
		except Exception, ex:
		    print ex
		    return None
	    return None
		
    def getdata_nfs_total_speed_bydir(self, queryname, *args, **kwargs):
	    if queryname == 'get_nas':
		try:
		    selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['servers']])
		    data   = self.connection.get_list(selstr)
		    return data
		except Exception, ex:
		    print ex
		    return None
	    return None
		    
  	
    
    def getdata_nfs_total_users_traf(self,  queryname, *args, **kwargs):
	if queryname == 'get_accounts':
	    selstr = dssdict[queryname] % 'IN (%s)' % ', '.join([str(aint) for aint in kwargs['users']])
	    data   = self.connection.get_list(selstr)
	    print data
	    return data
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_classes':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['classes']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_tarifs':
	    selstr = dssdict[queryname] % (args[0].isoformat(' '), args[0].isoformat(' '), args[1].isoformat(' '), "AND (account_id IN (%s))" % ', '.join([str(aint) for aint in kwargs['users']]))
	    data   = self.connection.get_list(selstr)
	    data   = [list(tuple) for tuple in data]
	    selstr = dssdict["get_usernames"] % 'IN (%s)' % ', '.join([str(aint) for aint in kwargs['users']])
	    users   = self.connection.get_list(selstr)
	    if not data: data = [['', []]]
	    for i in range(len(data)):		
		for valtup in users:
		    if data[i][0] == valtup[1]:
			data[i][0] = valtup[0]
			break
	    return data
	return None
    
    def getdata_nfs_total_users_speed(self,  queryname, *args, **kwargs):
	if queryname == 'get_accounts':
	    selstr = dssdict[queryname] % 'IN (%s)' % ', '.join([str(aint) for aint in kwargs['users']])
	    data   = self.connection.get_list(selstr)
	    return data
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_classes':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['classes']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	if queryname == 'get_tarifs':
	    selstr = dssdict[queryname] % (args[0].isoformat(' '), args[0].isoformat(' '), args[1].isoformat(' '), "AND (account_id IN (%s))" % ', '.join([str(aint) for aint in kwargs['users']]))
	    data   = self.connection.get_list(selstr)
	    data   = [list(tuple) for tuple in data]
	    selstr = dssdict["get_usernames"] % 'IN (%s)' % ', '.join([str(aint) for aint in kwargs['users']])
	    users   = self.connection.get_list(selstr)
	    if not data: data = [['', []]]
	    for i in range(len(data)):		
		for valtup in users:
		    if data[i][0] == valtup[1]:
			data[i][0] = valtup[0]
			break
	    return data
	return None
    def getdata_nfs_nas_traf(self, queryname, *args, **kwargs):
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % str(kwargs['servers'][0])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	return None
    def getdata_nfs_total_nass_traf(self, queryname, *args, **kwargs):
	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	return None
    
    def getdata_nfs_total_classes_speed(self, queryname, *args, **kwargs):
	if queryname == 'get_classes':
	    try:
		print "^^^^^^^^^^^^^^^^^^^^^^^^"
		selstr = dssdict[queryname] % ', '.join([str(int) for int in kwargs['classes']])
		print "^^^^^^^^^^^^^^^^^^^^^^^^"
		print selstr
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
    	if queryname == 'get_nas':
	    try:
		selstr = dssdict[queryname] % ', '.join([str(aint) for aint in kwargs['servers']])
		data   = self.connection.get_list(selstr)
		return data
	    except Exception, ex:
		print ex
		return None
	return None
    def getdata_usertrafpie(self, queryname, *args, **kwargs):
	return None
    def getdata_sessions(self, queryname, *args, **kwargs):
	return None
    def getdata_trans_deb(self, queryname, *args, **kwargs):
	return None
    def getdata_trans_crd(self, queryname, *args, **kwargs):
	return None