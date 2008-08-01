from datetime import datetime, timedelta

from matplotlib.dates import DateFormatter, SecondLocator, MinuteLocator, HourLocator, WeekdayLocator, DayLocator, MonthLocator, YearLocator, date2num  
from matplotlib.ticker import IndexLocator, FormatStrFormatter
from matplotlib.font_manager import FontProperties
import time
from bpbl import bpbl, selstrdict


plotvaldict = {'a':""}

#todo: make methods except bpdraw() private  ???
#todo: make a dictionary for default plotting values

class bpmplDrawer(object):
    '''Drawer: class for plotting'''

    #method handler
    def bpdraw(self, axes, *args):
	'''Plotting methods' handler
	@args[0] - method identifier'''
	method = getattr(self, "bpdraw_" + args[0], None)
	if callable(method): 
	    return method(axes, *args)
	else:
	    raise Exception("Plotting method #" + args[0] + "# does not exist!" )

    #plotting methods
    def bpdraw_nfs_user_traf(self, axes, *args):
	'''Plots traffic/time by traffic classes on
	@axes - axes, 
	@args[1] for a user @account_id, 
	@args[2] with values bounded by dates @date_start, 
	@args[3] @date_end, 
	@args[4] aggeregated by @sec'''
	try:
	    #get a string from #selstrdict# dictionary wit a key based on the method name and compute a query string from it 
	    selstr = selstrdict[args[0][:3]] % ('(account_id=%d) AND' % args[1], args[2].isoformat(' '), args[3].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, y_in, y_out, y_tr, bstr) = bpbl.get_traf(selstr, args[4]) 
	bstr = '%.1f ' + bstr
	#--------------------
	#get dates as numbers
	tsec = date2num(times)
	axes.hold(True)
	#plot
	axes.plot(tsec, y_in, color='blue', lw=1.3)
	axes.plot(tsec, y_tr, color='red', lw=1.3)
	axes.bar(tsec, y_out, width = (tsec[1] - tsec[0]), color='lime', edgecolor='none')
	#count total seconds to format the axes
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds	
	#get tics
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo)
	#format axes
	self.format_axes(axes, xmiloc, xmaloc, xfmt, bstr, ('INPUT', 'TRANSFER', 'OUTPUT'))

    def bpdraw_nfs_user_speed(self, axes, *args):
	'''Plots speed/time by traffic classes on
	@axes - axes,
	@args[1:4] - for a user @account_id, with values bounded by dates @date_start, @date_end and aggeregated by @sec'''
	#critical place
	try:
	    selstr = selstrdict[args[0][:3]] % ('(account_id=%d) AND' % args[1], args[2].isoformat(' '), args[3].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, y_in, y_out, y_tr, bstr) = bpbl.get_speed(selstr, args[4])  
	bstr = '%.1f ' + bstr
	#--------------------
	#get dates as numbers
	tsec = date2num(times)
	axes.hold(True)
	#plot
	axes.plot(tsec, y_in, color='blue', lw=1.3)
	axes.plot(tsec, y_tr, color='red', lw=1.3)
	axes.bar(tsec, y_out, width = (tsec[1] - tsec[0]), color='lime', edgecolor='none')
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds
	#print rttlsec

	#get tics
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo)  
	self.format_axes(axes, xmiloc, xmaloc, xfmt, bstr, ('INPUT', 'TRANSFER', 'OUTPUT'))

    def bpdraw_nfs_total_traf_bydir(self, axes, *args):
	'''Plots traffic/time by traffic classes for all users on
	@axes - axes,
	@args[1:3] - with values bounded by dates @date_start, @date_end and aggeregated by @sec'''
	try:
	    selstr = selstrdict[args[0][:3]] % ('', args[1].isoformat(' '), args[2].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, y_in, y_out, y_tr, bstr) = bpbl.get_traf(selstr, args[3]) 
	bstr = '%.1f ' + bstr
	#--------------------  
	tsec = date2num(times)
	axes.hold(True)
	axes.plot(tsec, y_in, color='blue', lw=1.3)
	axes.plot(tsec, y_tr, color='red', lw=1.3)
	axes.bar(tsec, y_out, width = (tsec[1] - tsec[0]), color='lime', edgecolor='none')
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds      
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo)  
	self.format_axes(axes, xmiloc, xmaloc, xfmt, bstr, ('INPUT', 'TRANSFER', 'OUTPUT'))

    def bpdraw_nfs_total_speed_bydir(self, axes, *args):
	'''Plots speed/time by traffic classes for all users on
	@axes - axes,
	@args[1:3] - with values bounded by dates @date_start, @date_end and aggeregated by @sec'''
	try:
	    selstr = selstrdict[args[0][:3]] % ('', args[1].isoformat(' '), args[2].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, y_in, y_out, y_tr, bstr) = bpbl.get_speed(selstr, args[3])  
	bstr = '%.1f ' + bstr
	#--------------------  
	tsec = date2num(times)
	axes.hold(True)
	axes.plot(tsec, y_in, color='blue', lw=1.3)
	axes.plot(tsec, y_tr, color='red', lw=1.3)
	axes.bar(tsec, y_out, width = (tsec[1] - tsec[0]), color='lime', edgecolor='none')
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds       
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo)  
	self.format_axes(axes, xmiloc, xmaloc, xfmt, bstr, ('INPUT', 'TRANSFER', 'OUTPUT'))


    def bpdraw_nfs_total_traf(self, axes, *args):
	'''Plots traffic/time for all users on
	@axes - axes,
	@args[1:3] - with values bounded by dates @date_start, @date_end and aggeregated by @sec'''
	try:
	    selstr = selstrdict[args[0][:3]] % ('', args[1].isoformat(' '), args[2].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, y_total, bstr) = bpbl.get_total_traf(selstr, args[3])	
	bstr = '%.1f ' + bstr
	#--------------------  
	tsec = date2num(times)
	axes.hold(True)

	axes.plot(tsec, y_total, color='brown', lw=1.3)
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds
	#print rttlsec        
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo)  
	self.format_axes(axes, xmiloc, xmaloc, xfmt, bstr, ('TOTAL'))

    def bpdraw_nfs_total_speed(self, axes, *args):
	'''Plots speed/time for all users on
	@axes - axes,
	args[1:3] - with values bounded by dates @date_start, @date_end and aggeregated by @sec'''
	try:
	    selstr = selstrdict[args[0][:3]] % ('', args[1].isoformat(' '), args[2].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, y_total, bstr) = bpbl.get_total_speed(selstr, args[3])	
	bstr = '%.1f ' + bstr
	#--------------------  
	tsec = date2num(times)
	axes.hold(True)

	axes.plot(tsec, y_total, color='brown', lw=1.3)
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds
	#print rttlsec        
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo)  
	self.format_axes(axes, xmiloc, xmaloc, xfmt, bstr, ('TOTAL'))

    def bpdraw_nfs_port_speed(self, axes, *args):
	'''Plots speed/time on
	@axes - axes,
	@args[1:4] - for port @port, with values bounded by dates @date_start, @date_end and aggeregated by @sec'''
	try:
	    selstr = selstrdict[args[0]] % (args[1], args[1], args[2].isoformat(' '), args[3].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, y_ins, y_outs, y_ind, y_outd, bstr) = bpbl.get_port_speed(selstr, args[4], args[1])
	bstr = '%.1f ' + bstr
	#--------------------  
	tsec = date2num(times)
	axes.hold(True)

	axes.plot(tsec, y_ins,  color='blue')
	axes.plot(tsec, y_outs, color='lime')
	#axes.bar(tsec, y_outs, width = (tsec[1] - tsec[0]), color='lime', edgecolor='none')        
	axes.plot(tsec, y_ind,  color='firebrick')
	axes.plot(tsec, y_outd, color='magenta')
	#axes.bar(tsec, y_outd, width = (tsec[1] - tsec[0]), color='magenta', edgecolor='none')
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds
	#print rttlsec        
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo)  
	self.format_axes(axes, xmiloc, xmaloc, xfmt, bstr, ('INPUT SRC','OUTPUT SRC', 'INPUT DEST', 'OUTPUT DEST'))

    def bpdraw_userstrafpie(self, axes, *args):
	'''Plots pie chart of traffic values on
	@axes - axes,
	@args[1:3] - with values bounded by dates @date_start, @date_end for users @(users)'''
	try:
	    selstr = selstrdict[args[0]] % (args[1].isoformat(' '), args[2].isoformat(' '), str(args[3]))	
	except Exception, ex:
	    raise ex
	(x, labels) = bpbl.get_pie_traf(selstr)
	explode = [0.025 for i in range(len(args[3]))]
	colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')
	axes.pie(x, labels=labels, explode=explode, shadow=True, colors=colors)

    def bpdraw_sessions(self, axes, *args):
	'''Plots bar chart of sessions/time on
	@axes - axes,
	@args[1:3] - for user = @account_id, with values bounded by dates @date_start, @date_end'''
	try:
	    selstr = selstrdict[args[0]] % (args[1], args[2].isoformat(' '), args[3].isoformat(' '), args[2].isoformat(' '), args[3].isoformat(' '))
	except Exception, ex:
	    raise ex
	(t_start, t_end, sessid) = bpbl.get_sessions(selstr)
	n_start = date2num(t_start)
	n_end = date2num(t_end)
	n_width = n_end - n_start
	dstz = args[2].replace(tzinfo=t_start[0].tzinfo)
	detz = args[3].replace(tzinfo=t_start[0].tzinfo)
	axes.hold()
	axes.barh(range(len(n_start)), n_width, 0.1, left=n_start)
	rsec = detz - dstz
	rttlsec = rsec.days*3600*24 + rsec.seconds
	#print rttlsec
	rttlsec *=3

	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(t_start[0].tzinfo)
	self.format_sess_axes(axes, xmiloc, xmaloc, xfmt, dstz, detz, sessid)



    def bpdraw_trans_deb(self, axes, *args):
	'''Plots bar chart of debit transactions/time on
	@axes - axes,
	@args[1:2] - for all users, with values bounded by dates @date_start, @date_end'''
	try:
	    selstr = selstrdict[args[0][:5]] % ('> 0', args[1].isoformat(' '), args[2].isoformat(' '))
	except Exception, ex:
	    raise ex	
	(times, summ, bstr) = bpbl.get_trans(selstr, args[3], 'deb')
	bstr = '%.1f ' + bstr
	tsec = date2num(times)
	axes.bar(tsec, summ, width = (tsec[1] - tsec[0]))
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds
	#print rttlsec
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo )
	#--------------------
	self.format_axes(axes, xmaloc, xmiloc, xfmt, bstr)

    def bpdraw_trans_crd(self, axes, *args):
	'''Plots bar chart of credit transactions/time on
	@axes - axes,
	@args[1-2] - for all users, with values bounded by dates @date_start, @date_end'''
	try:
	    selstr = selstrdict[args[0][:5]] % ('< 0', args[1].isoformat(' '), args[2].isoformat(' '))
	except Exception, ex:
	    raise ex
	(times, summ, bstr) = bpbl.get_trans(selstr, args[3], 'crd')
	bstr = '%.1f ' + bstr
	tsec = date2num(times)
	axes.bar(tsec, summ, width = (tsec[1] - tsec[0]))
	rsec = times[-1] - times[0]
	rttlsec = rsec.days*3600*24 + rsec.seconds
	#print rttlsec
	(xmiloc, xmaloc, xfmt) = self.format_ticks(rttlsec)
	xfmt.set_tzinfo(times[0].tzinfo )
	#--------------------
	self.format_axes(axes, xmaloc, xmiloc, xfmt, bstr)




       # tick formatting methods
    def format_ticks(self, rttlsec):
	'''Formats X axis/ticks according to time values
	@rttlsec - time span converted to seconds'''
	if rttlsec < 120:
	    xmiloc = SecondLocator((10, 20, 30, 40, 50))
	    xmaloc = MinuteLocator()
	    xfmt = DateFormatter("%d %H:%M")            
	elif  120 < rttlsec <= 300:
	    xmiloc = SecondLocator((30))
	    xmaloc = MinuteLocator()
	    xfmt = DateFormatter("%d %H:%M")
	elif  300 < rttlsec <= 1800:
	    xmiloc = MinuteLocator((0, 3, 6, 9 ,12, 15, 18, 21, 24, 27, 33, 36, 39, 42, 45, 48, 51, 54, 57))
	    xmaloc = MinuteLocator()
	    xfmt = DateFormatter("%d %H:%M")
	elif 1800 < rttlsec <= 3600:
	    xmiloc = MinuteLocator()
	    xmaloc = MinuteLocator((0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55)) 
	    xfmt = DateFormatter("%d %H:%M")
	elif 3600 < rttlsec <= 10800:
	    xmiloc = MinuteLocator((0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55))
	    xmaloc = MinuteLocator((0, 10, 20, 30, 40, 50)) 
	    xfmt = DateFormatter("%d %H:%M")
	elif 10800 < rttlsec <= 32400:
	    xmaloc = MinuteLocator((30))
	    xmiloc = HourLocator() 
	    xfmt = DateFormatter("%d %H:%M")
	elif 32400 < rttlsec <= 86400: #day
	    #xmiloc = HourLocator((0, 3, 6, 9, 12, 15, 18, 21))
	    xmiloc = HourLocator() 
	    xmaloc = HourLocator((0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22))  
	    xfmt = DateFormatter("%d %H:00")
	elif 86400 < rttlsec <= 259200: 
	    xmaloc = HourLocator((3, 9, 15, 21))
	    xmiloc = HourLocator((0, 6, 12, 18))
	    xfmt = DateFormatter("%m-%d %H:00")
	elif 259200 < rttlsec <= 604800: 
	    xmiloc = HourLocator(interval=12)
	    xmaloc = HourLocator(interval=6)
	    xfmt = DateFormatter("%m-%d %H:00")
	elif 604800 < rttlsec <= 1339200: 
	    xmaloc = DayLocator()
	    xmiloc = HourLocator(interval=12)
	    xfmt = DateFormatter("%m-%d")
	elif 1339200 < rttlsec <= 2678400: #month
	    xmaloc = DayLocator()
	    xmiloc = DayLocator(interval=2)            
	    xfmt = DateFormatter("%m-%d")
	elif 2678400 < rttlsec <= 8035200: #quarter
	    xmiloc = DayLocator(interval=6) 
	    xmaloc = DayLocator(interval=3)  
	    xfmt = DateFormatter("%Y-%m-%d") 
	elif 8035200 < rttlsec <= 16070400: #half
	    xmaloc = WeekdayLocator() 
	    xmiloc = WeekdayLocator(interval=2) 
	    xfmt = DateFormatter("%Y-%m-%d") 
	elif 16070400 < rttlsec <= 32140800: #year
	    xmiloc = WeekdayLocator(interval=4)
	    xmaloc = WeekdayLocator(interval=2) 
	    xfmt = DateFormatter("%Y-%m-%d")            
	else:
	    xmiloc = MonthLocator()
	    xmaloc = MonthLocator() 
	    xfmt = DateFormatter("%Y-%m")
	return (xmiloc, xmaloc, xfmt)

    # axes formatting methods
    def format_axes(self, axes, xmiloc, xmaloc, xfmt, yformstr=None, legend=None):
	'''Formats X/Y axes by applying ticks and labels with 
	@xmiloc - minor formatter, 
	@xmaloc - major formatter, 
	@xfmt - X labels formater, 
	@yformstring - formatter string, 
	@legend'''
	axes.set_xticklabels((), fontsize='smaller')
	min_t_y = list(axes.get_yticks())[1]
	ymiloc = IndexLocator(min_t_y, min_t_y / 2)
	axes.yaxis.set_minor_locator(ymiloc)
	#set formatters and locators
	if yformstr:
	    yfmt = FormatStrFormatter(yformstr)
	axes.yaxis.set_major_formatter(yfmt)
	axes.xaxis.set_major_locator(xmaloc)
	axes.xaxis.set_major_formatter(xfmt)
	axes.xaxis.set_minor_locator(xmiloc)
	#set up grid
	axes.xaxis.grid(True, 'minor', alpha=0.3)
	axes.yaxis.grid(True, 'minor', alpha=0.3)
	axes.grid(True)
	if legend:
	    axes.legend(legend, prop = FontProperties(size='smaller'))
	#autoformate date
	axes.figure.autofmt_xdate()

    def format_sess_axes(self, axes, xmiloc, xmaloc, xfmt, dstz, detz, sessid):
	'''Formats axes for #sessions# plot
	@xmiloc - minor formatter, 
	@xmaloc - major formatter, 
	@xfmt - X labels formater,
	@dstz - date_start
	@detz - date_end
	@sessid - id's for Y labels'''
	axes.set_xticklabels((), fontsize='smaller')	
	axes.xaxis.set_major_locator(xmaloc)
	axes.xaxis.set_major_formatter(xfmt)
	axes.xaxis.set_minor_locator(xmiloc)
	xticks = axes.get_xticks().tolist()
	xticks.append(date2num(dstz))
	xticks.append(date2num(detz))
	xticks.sort()
	axes.set_xticks(xticks)
	yticks = axes.get_yticks().tolist()
	if len(yticks) > len(sessid):
	    while len(yticks) > len(sessid):
		yticks.pop()
	axes.set_yticklabels(sessid, fontsize='smaller')        
	axes.xaxis.grid(True, 'minor', alpha=0.3)
	#axes.yaxis.grid(True, 'minor', alpha=0.3)
	axes.grid(True)
	axes.axvline(date2num(dstz), color='r', label=dstz.strftime(xfmt.fmt))
	axes.axvline(date2num(detz), color='r', label=detz.strftime(xfmt.fmt))
	axes.figure.autofmt_xdate()
