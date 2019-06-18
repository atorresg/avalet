import pickle, os, sys
from pathlib import Path
class Avalet:

    homedir = str(Path.home())
    vars = {'tld':'.test','domains':{}}

    def __init__(self):
        self.config_dir=self.homedir+'/.config/avalet/'
        if not Path.is_dir(Path(self.homedir+'/.config/avalet')):
            self.install()
        else:
            self.loadVars()

    def install(self):
        os.system('brew list httpd &>/dev/null && echo "Apache server installed" || brew install httpd')
        os.system('brew list dnsmasq &>/dev/null && echo "dnsmasq installed" || brew install dnsmasq')
        if not Path.is_dir(Path(self.homedir+'/.config')):
            Path(self.homedir+'/.config').mkdir(0o755)
        if not Path.is_dir(Path(self.homedir+'/.config/avalet')):
            Path(self.homedir+'/.config/avalet').mkdir(0o755)
        if not Path.is_dir(Path(self.homedir+'/.config/avalet/logs')):
            Path(self.homedir+'/.config/avalet/logs').mkdir(0o755)
        if not Path.is_dir(Path(self.homedir+'/.config/avalet/certificates')):
            Path(self.homedir+'/.config/avalet/certificates').mkdir(0o755)
        if not Path.is_dir(Path(self.homedir+'/.config/avalet/httpd')):
            Path(self.homedir+'/.config/avalet/httpd').mkdir(0o755)
        if not Path.is_file(Path(self.homedir+'/.config/avalet/vars')):
            Path(self.homedir+'/.config/avalet/vars').touch(0o644)
            self.updateVars()
        
        with open('/usr/local/etc/dnsmasq.conf','r') as f:
            if not 'conf-file='+self.homedir+'/.config/avalet/dnsmasq.conf' in f.read():
                f.close
                f = open('/usr/local/etc/dnsmasq.conf','a')
                f.write('conf-file='+self.homedir+'/.config/avalet/dnsmasq.conf')
        f.close()
        if not Path.is_file(Path(self.homedir+'/.config/avalet/dnsmasq.conf')):
            Path(self.homedir+'/.config/avalet/dnsmasq.conf').touch(0o644)
            self.updateTLD(self.vars['tld'])
    
    def updateVars(self):
        with open(self.homedir+'/.config/avalet/vars','wb') as f:
            pickle.dump(self.vars,f)

    def loadVars(self):
        with open(self.homedir+'/.config/avalet/vars','rb') as f:
            self.vars=pickle.load(f)

    def updateTLD(self,name):
            f = open (self.homedir+'/.config/avalet/dnsmasq.conf','w+')
            f.write ("address=/"+name+"""/127.0.0.1
listen-address=127.0.0.1""")

    def unlink(self,domain):
        if self.vars['domains'][domain]['secure']:
            Path(self.config_dir+'/certificates/'+domain+self.vars['tld']+'.key').unlink()
            Path(self.config_dir+'/certificates/'+domain+self.vars['tld']+'.crt').unlink()
        Path(self.config_dir+'/httpd/'+domain+'.conf').unlink()
        del self.vars['domains'][domain]
        self.updateVars()
        os.system('brew services restart httpd')

    def secure(self,domain):
        dirpath = os.getcwd()
        config_dir = self.homedir+'/.config/avalet/'
        vhost="""
Listen 443  
<VirtualHost {name}{tld}:443>
    ServerName {name}{tld}
    DocumentRoot "{docroot}"
    SSLEngine on
    SSLCertificateFile "{dir}{name}{tld}.crt"
    SSLCertificateKeyFile "{dir}{name}{tld}.key"
</VirtualHost>""".format_map({'name':domain,'docroot':dirpath,'dir':config_dir+'certificates/','tld':self.vars['tld']})
        cert="""openssl req  -nodes -new -x509  -keyout {dir}{name}{tld}.key -out {dir}{name}{tld}.crt"""
        os.system(cert.format_map({'name':domain,'dir':self.config_dir+'certificates/','tld':self.vars['tld']}))
        file=config_dir+'httpd/'+domain+'.conf'
        f = open (file, 'a')
        f.write(vhost)
        f.close()
        self.vars['domains'][domain]['secure']=True
        self.updateVars()
        os.system('brew services restart httpd')
    def getDomain(self):
        dirpath = os.getcwd()
        try:
            sys.argv[2]
        except IndexError:
            domain = os.path.basename(dirpath)
        else:
            domain = sys.argv[2]
        return domain
