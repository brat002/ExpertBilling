import datetime, commands
        
F_NAME = 'TEXT_REP'
NAME_PREF = 'netflow.'
STRFTEMPLATE = '%Y-%m-%d_%H-%M'

DEF_FILE_NUM = 100
SCRIPT_STR = """ls -1 %s | mawk 'BEGIN {lines = 0}; $0 >= "%s" && $0 <= "%s" { print $0; lines +=1; if (lines >=""" + str(DEF_FILE_NUM) + """) exit }'"""
DATA_SCRIPT_STR = """mawk 'BEGIN {FS = ","; lines = 0; filename = ""; %s}; %s {print $21,$1,$10,$2,$11,$7,$22; lines = lines + 1; if (filename != FILENAME) {if (lines >= %s) {print FILENAME; exit} else {filename = FILENAME}}}' %s"""

calc_fname = lambda file_date: ''.join((NAME_PREF, file_date.strftime(STRFTEMPLATE)))

def get_data_string(data_string, options_list):
    if options_list[0] == 'none':
        return data_string % ('', '', '%s', '%s')
    elif options_list[0] == 'accounts':
        return data_string % ('''acc_num = split("%s", accounts, ","); for (item in accounts) {accounts[accounts[item]] = 1; delete accounts[item]};''' % options_list[1],
                              '$21 in accounts', '%s', '%s')

def get_files(flow_dir, start_filename, end_filename, script_str):
    return commands.getstatusoutput(script_str % (flow_dir, start_filename, end_filename))
    #[0].split('/n')
    
def get_new_files(textReportInfo):
    if textReportInfo.command == 'next':
        if not textReportInfo.got_more_files:
            textReportInfo.files = []
            return
        if not textReportInfo.start_dates:
            textReportInfo.start_dates.append(textReportInfo.start_date)
        #textReportInfo.got_more_files = True
        """
    elif textReportInfo.command == 'home':
        textReportInfo.start_dates = []
        textReportInfo.start_dates.append(textReportInfo.start_date)
        """
    elif  textReportInfo.command == 'prev':
        textReportInfo.start_dates.pop()
        textReportInfo.start_dates.pop()
        if not textReportInfo.start_dates:
            textReportInfo.files = []
            return
        
    start_date = textReportInfo.start_dates[-1]
    fl_out = get_files(textReportInfo.flow_dir, calc_fname(start_date), 
                       calc_fname(textReportInfo.end_date), SCRIPT_STR)
    if fl_out[0] != 0:
        raise Exception('Text report: get file error: %s' % fl_out[0])
    textReportInfo.files = fl_out[1].split('\n')
    if textReportInfo.command == 'next':
        if fl_out[1].count('\n') < DEF_FILE_NUM - 1:
            textReportInfo.got_more_files = False
    if not textReportInfo.files: return
    last_str = textReportInfo.files[-1]
    f_date = datetime.datetime.strptime(last_str[last_str.find(NAME_PREF) + len(NAME_PREF):], STRFTEMPLATE)
    textReportInfo.start_dates.append(f_date)
        
    
def get_data(textReportInfo):
    #check awk for file options
    take_index = textReportInfo.last_file_num[-1]
    data_strs = []
    total_count = 0
    while True:
        if total_count >= textReportInfo.take_data_by:
            break
        if not textReportInfo.files:
            raise Exception('Text report: no more files!')
        fnames = map(lambda x: ''.join((textReportInfo.flow_dir, x)), textReportInfo.files[take_index:textReportInfo.take_files_by])
        if not fnames:
            get_new_files(textReportInfo)
            continue                
        scr_output = commands.getstatusoutput(textReportInfo.data_script % ' '.join(fnames))
        if scr_output[0] != 0:
            raise Exception('Text report: get data error: %s' % scr_output[0] )
        if not scr_output[1]:
            take_index += + len(fnames)
            continue
        data_str = scr_output[1]
        last_str_index = data_str.rfind('\n')
        if last_str_index == -1:
            take_index += len(fnames)
            data_strs.append(data_str)
            total_count +=1
            continue
        last_str = data_str[last_str_index+1:]
        if last_str.find(textReportInfo.name_prefix) == -1:                    
            take_index += len(fnames)
        else:
            take_index += fnames.index(last_str)
            data_str = data_str[:last_str_index]
        
        total_count += data_str.count('\n') + 1
        data_strs.append(data_str)
    return (take_index, '\n'.join(data_strs).split('\n'))

def get_saved_data(textReportInfo):
    if textReportInfo.command == 'next':
        ret_data = None
        if (textReportInfo.read_data and not textReportInfo.last_datum_num[-1] < textReportInfo.read_data_num) \
           or not textReportInfo.read_data:
            #textReportInfo.read_data  = []
            textReportInfo.last_datum_num = [0]
            #textReportInfo.read_data_num = 0
            file_num, read_data = get_data(textReportInfo)
            textReportInfo.read_data  = read_data
            textReportInfo.read_data_num = len(read_data)
            textReportInfo.last_file_num.append(file_num)
        ret_data = textReportInfo.read_data[textReportInfo.last_datum_num[-1]:textReportInfo.last_datum_num[-1]+textReportInfo.take_data_by]
        textReportInfo.last_datum_num.append(textReportInfo.last_datum_num[-1] + len(ret_data))
        return ret_data
    elif textReportInfo.command == 'prev':
        if textReportInfo.last_datum_num == [0]:
            if textReportInfo.last_file_num == [0]:
                get_new_files(textReportInfo)
            else:
                textReportInfo.last_file_num.pop()
                textReportInfo.last_file_num.pop()
                if not textReportInfo.last_file_num:
                    textReportInfo.last_file_num = [0]
            textReportInfo.last_datum_num = [0]
            file_num, read_data = get_data(textReportInfo)
            textReportInfo.read_data  = read_data
            textReportInfo.read_data_num = len(read_data)
            textReportInfo.last_file_num.append(file_num)
        else:
            textReportInfo.last_datum_num.pop()
            textReportInfo.last_datum_num.pop()
            if not textReportInfo.last_datum_num:
                textReportInfo.last_datum_num = [0]
        ret_data = textReportInfo.read_data[textReportInfo.last_datum_num[-1]:textReportInfo.last_datum_num[-1]+textReportInfo.take_data_by]
        textReportInfo.last_datum_num.append(textReportInfo.last_datum_num[-1] + len(ret_data))
        return ret_data
    else:
        raise Exception('Text report: unknown command %s!' % textReportInfo.command)
            
class TextReportInfo(object):

    def __init__(self, start_date, end_date, data_options, rep_type, flow_dir):
        self.start_date = None
        self.end_date   = None
        self.current_data_file = None
        self.got_more_files = True
        self.files      = []
        self.start_dates = []
        self.last_file_num = [0]
        self.got_more_data = False
        self.read_data  = []
        self.last_datum_num = [0]
        self.read_data_num = 0
        self.data_script = ''
        self.flow_dir = ''
        self.name_prefix = 'netflow.'
        self.take_files_by = 20
        self.take_data_by = 2000
        self.command = ''
        #----------------
        self.start_date = start_date
        self.end_date = end_date
        self.command = rep_type
        self.flow_dir = flow_dir
        self.data_script = get_data_string(DATA_SCRIPT_STR, data_options) % (self.take_data_by, '%s')
    def clear(self):
        self.got_more_files = True
        self.files = []
        self.start_dates = []
        self.last_file_num = [0]
        self.got_more_data = False
        self.read_data  = []
        self.last_datum_num = [0]
        self.read_data_num = 0
        