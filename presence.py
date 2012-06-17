from werkzeug.wrappers import Request, Response
import paramiko, base64, pickle, os, logging

@Request.application
def application(request):
    logger = logging.getLogger('presence_detection')
    logger.setLevel(logging.info)
    fh = logging.FileHandler('~/presence2/log/presence_detection.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    key = paramiko.RSAKey(data=base64.decodestring('AAAAB3NzaC1yc2EAAAADAQABAAAAgwCjvHkbqL/V0ytnfa5pIak7bxBfj6nF4S7vy51ZG8LlWYAXcQ9WGfUGfhG+l1GW9hPeQzQbeRyNiQM+ufue/M9+JKCXTIugksAnN3W+NV/DeDcq9sKR9MiiNH3ZeNtGSyPGYjcLVmK6aSVTUoEO2yRrha9fiWBy5hb93UdmJX+QguC9'))
    client = paramiko.SSHClient()
    client.get_host_keys().add('[makerbar.berthartm.org]:2222', 'ssh-rsa', key)
    wlauthkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/presence2/keys/wlauth'))
    client.connect('makerbar.berthartm.org', username='root', port=2222, pkey=wlauthkey)
    stdin, stdout, stderr = client.exec_command('wl assoclist')
    usermap = get_dict()
    attendance = set()
    for line in stdout:
        MAC = line[10:27]
        if MAC in usermap:
            attendance.add(usermap[MAC])
            logger.info(usermap[MAC]+'('+MAC+') is at the MakerBar.')
        else:
            logger.info('Unknown user('+MAC+') is at the MakerBar.')	    

    output = ''
    for user in attendance:
        output += user + '\n'
    response = Response(output)
    if output == '':
        response.status_code = 204 # No content
    client.close()
    return response

def get_dict():
    with open(os.path.expanduser('~/presence/macs.pckl')) as f:
        d = pickle.load(f)
    return d

if __name__ == '__main__':
   from werkzeug.serving import run_simple
   run_simple('localhost', 4000, application)
