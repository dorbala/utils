
#!/usr/bin/python

import sys
import os
import pexpect
import pxssh
import getpass
import socket

# IMP: Assumes pexpect is installed!
# host1.zip, host2.zip, etc. contain the respective rsa/dsa keys
# Extract host1.zip, host2.zip, .. in host1's directory before running the script
# Run the script at the source

# USAGE: ./pwdless_ssh.py <user_name> <src_name> <dest_name>

USER=sys.argv[1]
HOSTS=sys.argv[2:]
src=socket.gethostname()

print 'User to be configured is %s' %USER
print 'HOSTS being configured for pwdless ssh are %s' %HOSTS

for host in HOSTS:
    print 'configuring host %s..'
    password=getpass.getpass('password for ssh to %s as user %s:' %(host,USER))
    if host==src:
       zip_file='host1.zip'
    else:
       dest=host
       zip_file='host2.zip' 

    child = pexpect.spawn('scp %s:~/%s %s:~' %(src,zip_file,host))
    i = child.expect(["password:",pexpect.EOF])

    if i==0:
       child.sendline(password)
       child.expect(pexpect.EOF)

    s=pxssh.pxssh()
    #password=getpass.getpass('password for ssh to %s as user %s:' %host %USER)
    if s.login(host,USER,password):
      s.sendline('rm -rf .ssh/')
      s.sendline('unzip %s' %zip_file) 
      s.sendline('touch .ssh/config')
      s.sendline('echo \\StrictHostKeyChecking no\\ >> .ssh/config')
      s.sendline('chmod 755 .ssh')
      s.sendline('chmod 600 .ssh/authorized_keys')
      s.sendline('cat .ssh/*.pub >> .ssh/authorized_keys')
      s.sendline('ssh %s' %host)
      s.sendline('exit')
      s.prompt()
      s.logout()
    else:
      print "SSH Failed"


s=pxssh.pxssh()
if s.login(dest,USER,''):
    s.sendline('scp %s:~/.ssh/known_hosts ~/.ssh/.' %src)
    s.logout()
else:
    print "SSH Failed"
