from werkzeug.wrappers import Request, Response
import paramiko, base64, pickle, os, logging

@Request.application
def application(request):
    logger = logging.getLogger('presence_detection')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.expanduser('~/presence2/log/presence_detection.log'),mode='a', encoding=None, delay=False)
    formatter = logging.Formatter('%(asctime)s - %(levelname)r - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    rsa_key='AAAAB3NzaC1yc2EAAAADAQABAAAAgwCjvHkbqL/V0ytnfa5pIak7bxBfj6nF4S7vy51ZG8LlWYAXcQ9WGfUGfhG+l1GW9hPeQzQbeRyNiQM+ufue/M9+JKCXTIugksAnN3W+NV/DeDcq9sKR9MiiNH3ZeNtGSyPGYjcLVmK6aSVTUoEO2yRrha9fiWBy5hb93UdmJX+QguC9'
    router_address='makerbar.berthartm.org'
    router_port = 2222
    stdin, stdout, stderr =get_router_mac_addresses(rsa_key,router_address,router_port)

    usermap = get_dict()
    attendance = set()
    for line in stdout:
        MAC = line[10:27]
        if MAC in usermap:
            attendance.add(usermap[MAC])
            logger.info('%s (%s) is at the MakerBar.' % (usermap[MAC],MAC))
        else:
            logger.info('Unknown user(%s) is at the MakerBar.' % MAC)

    output = ''
    for user in attendance:
        output += user + '\n'
    response = Response(output)
    if output == '':
        response.status_code = 204 # No content

    fh.close()
    return response

def get_dict():
    with open(os.path.expanduser('~/presence/macs.pckl')) as f:
        d = pickle.load(f)
    return d

def get_router_mac_addresses(rsa_key,router_address,router_port):
    key = paramiko.RSAKey(data=base64.decodestring(rsa_key))
    client = paramiko.SSHClient()
    client.get_host_keys().add('[%s]:%d' % (router_address,router_port), 'ssh-rsa', key)
    wlauthkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/presence2/keys/wlauth'))
    client.connect(router_address, username='root', port=router_port, pkey=wlauthkey)
    stdin, stdout, stderr = client.exec_command('wl assoclist')
    client.close()
    return stdin, stdout, stderr


if __name__ == '__main__':
   from werkzeug.serving import run_simple
   run_simple('localhost', 4000, application)
