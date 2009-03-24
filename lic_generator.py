from random import choice
from string import ascii_letters, digits

import sys

let_seq = ascii_letters + digits

if __name__ == '__main__':
    proj_name = sys.argv[1]
    users = sys.argv[2]
    hex_users = '0000'
    if users == 'unlimited':
        hex_users = 'FFFF'
    else:
        hex_users = hex(int(users))[2:].zfill(4).upper()
        
    main_str = ''
    for i in xrange(12):
        main_str += choice(let_seq)
        
    main_str = (hex_users[0:2] + main_str + hex_users[2:4]).upper()
    
    f = open('license_' + proj_name + '.lic', 'wb')
    
    f.write(main_str)
    f.close()