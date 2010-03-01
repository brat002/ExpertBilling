import datetime   
        
F_NAME = 'TEXT_REP'
NAME_PREF = 'netflow.'
STRFTEMPLATE = '%Y-%m-%d_%H-%M'

DEF_FILE_NUM = 100
SCRIPT_STR = """ls -1 %s | mawk 'BEGIN {lines = 0}; $0 => "%s" && $0 <= "%s" { print $0; lines +=1; if (lines >=""" + str(DEF_FILE_NUM) + """) exit }'"""
DATA_SCRIPT_STR = """mawk 'BEGIN {FS = ","; lines = 0; filename = ""; -- acc_num = split("338,368", accounts, ","); for (item in accounts) {accounts[accounts[item]] = 1; delete accounts[item]};--}; --$21 in accounts-- {print $21,$1,$10,$2,$11,$7,$22; lines = lines + 1; if (filename != FILENAME) {if (lines >= %s) {print FILENAME; exit} else {filename = FILENAME}}}'"""

calc_fname = lambda file_date: ''.join((NAME_PREF, file_date.strftime(STRFTEMPLATE)))


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
    elif textReportInfo.command == 'home':
        textReportInfo.start_dates = []
        textReportInfo.start_dates.append(textReportInfo.start_date)
    elif  textReportInfo.command == 'prev':
        textReportInfo.start_dates.pop()
        textReportInfo.start_dates.pop()
        if not textReportInfo.start_dates:
            textReportInfo.files = []
            return
        
    start_date = textReportInfo.start_dates[-1]
    fl_out = get_files(textReportInfo.flow_dir, calc_fname(start_date), 
                       calc_fname(textReportInfo.end_date, SCRIPT_STR))
    if fl_out[0]:
        raise Exception('Text report: get file error')
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
            get_new_files
            continue                
        scr_output = commands.getstatusoutput(textReportInfo.data_script % ','.join(fnames))
        if scr_output[0]:
            raise Exception('Text report: get data error!')
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
        
        total_count += data_str.count('\n')
        data_strs.append(data_str)
    return (take_index, total_count, '\n'.join(data_strs).split['\n'])

def get_saved_data(textReportInfo):
    return textReportInfo.read_data[textReportInfo.last_datum_num[-1], textReportInfo.take_data_by]
            
class TextReportInfo(object):
    start_date = None
    end_date   = None
    current_data_file = None
    got_more_files = True
    files      = []
    start_dates = []
    last_file_num = [0]
    got_more_data = False
    read_data  = []
    last_datum_num = [0]
    read_data_num = 0
    data_script = ''
    flow_dir = ''
    name_prefix = 'netflow.'
    take_files_by = 20
    take_data_by = 2000
    command = ''
    executed = ''
    def __init__(self, start_date, end_date, rep_type, flow_dir):
        pass