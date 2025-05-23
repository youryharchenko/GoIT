class IDException(Exception):
    pass


def add_id(id_list, employee_id: str):
    if employee_id.startswith('01'):
        id_list.append(employee_id)
    else:
        raise IDException

ids = []    
try:
    add_id(ids,  'aaa')
except IDException:
    print('IDException raised')

try:
    add_id(ids,  '01 aaa')
except IDException:
    print('IDException raised')
else:
    print('ok')
    
