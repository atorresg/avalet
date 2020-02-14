import pickle, os, sys
from pathlib import Path
from termcolor import colored
from shutil import which
from subprocess import Popen
from unidecode import unidecode

class Avalet:

    homedir = str(Path.home())
    vars = {'tld':'.test','domains':{}}

    def __init__(self):
        self.config_dir=self.homedir+'/.config/avalet/'
        if Path.is_file(Path(self.homedir+'/.config/avalet/vars')):
            self.loadVars()
        else:
            self.install()

    def checkinstall(self):
        if not Path.is_dir(Path(self.homedir+'/.config/avalet')):
            return False
        return True

    # create paths for config files
    def makedir(self,path):
        if not Path.is_dir(Path(self.homedir+path)):
            Path(self.homedir+path).mkdir(0o755)

    def help(self):
        print("""Avalet lets you use a local domain custom folders.
        Run """+colored('avalet install','green', attrs=['bold'])+""" first and then """+ colored('avalet link  DOMAIN','green',attrs=['bold'])+""" to link current directory to DOMAIN.test""")
        self.menu()

    def menu(self):
        print("""
        Must use one of the following parameters:
        """
        +colored("install:           ",'green', attrs=['bold'])+"""installs avalet and dependencies (dnsmasq and httpd)
        """
        +colored("reinstall:           ",'green', attrs=['bold'])+"""reinstalls avalet and dependencies (dnsmasq and httpd)
        """
        +colored("stop:           ",'green', attrs=['bold'])+"""stops services (dnsmask, apache and php)
        """
        +colored("start:           ",'green', attrs=['bold'])+"""starts services (dnsmask, apache and php)
        """
        +colored("restart:           ",'green', attrs=['bold'])+"""restart services (dnsmask, mysql and php)
        """
        +colored("list:           ",'green', attrs=['bold'])+"""list all linked domains
        """
        +colored("link [domain]:     ",'green', attrs=['bold'])+"""creates a domain with the same name as the actual path basename plus tld or a name given as aditional parameter
        """
        +colored("unlink [domain]:   ",'green', attrs=['bold'])+"""deletes a domain with the same name as the actual path basename plus tld or a name given as aditional parameter
        """
        +colored("secure [domain]:   ",'green', attrs=['bold'])+"""adds self signed ssl certificate. Browser must be forced to load url even if seurity warning is shown
        """
        +colored("tld [name]:        ",'green', attrs=['bold'])+"""changes current tld
        """)

    # installs packages if needed, config files and initial setup         
    def install(self):
        if self.checkinstall()==False:
            # check Homebrew is installed
            if which('brew') is None:
                print(colored("Homebrew not installed.",'red', attrs=['bold']))
                print('do you want to install Homebrew? Y/n')
                res = input()
                if (res.lower()!='n'):
                    os.system('mkdir homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C homebrew && rm -rf homebrew')
                else:
                    sys.exit('Homebrew is needed to install avalet')

            # prepare directory structure
            self.makedir('/.config')
            self.makedir('/.config')
            self.makedir('/.config/avalet')
            self.makedir('/.config/avalet/logs')
            self.makedir('/.config/avalet/certificates')
            self.makedir('/.config/avalet/httpd')

            # check if Dnsmasq is installed
            if which('dnsmasq') is None:
                print('Installing '+colored("Dnsmasq",'green', attrs=['bold'])+'...')
                os.system('brew install dnsmasq;')

            # set up Dnsmasq
            if not Path.is_dir(Path('/etc/resolver')):
                os.system('sudo mkdir /etc/resolver')
            if not Path.is_file(Path('/usr/local/etc/dnsmasq.conf')):
                os.system('sudo cp /usr/local/etc/dnsmasq.conf.default /usr/local/etc/dnsmasq.conf')
            os.system('sudo chmod 764 /usr/local/etc/dnsmasq.conf')
            with open('/usr/local/etc/dnsmasq.conf','r') as f:
                if not 'conf-file='+self.homedir+'/.config/avalet/dnsmasq.conf' in f.read():
                    f.close()
                    os.system('sudo echo "conf-file='+self.homedir+'/.config/avalet/dnsmasq.conf" > /usr/local/etc/dnsmasq.conf')
            f.close()

            # check if Apache is installed
            if which('httpd') is None:
                print('Installing '+colored("Apache",'green', attrs=['bold'])+'...')
                os.system('brew install httpd;')

            # if Apache is installed, check if it was installed through Homebrew
            elif not Path.is_dir(Path('/usr/local/Cellar/httpd/')):
                print('Apache is not found or not installed by Homebrew.')
                print('Do you want to replace it with Homebrew one? (recomended) Y/n')
                res = input()
                if (res.lower()!='n'):
                # uninstall default MacOS Apache, may be of use 
                    os.system('sudo apachectl stop')
                    os.system('sudo launchctl unload -w /System/Library/LaunchDaemons/org.apache.httpd.plist')
                    print('Installing '+colored("Apache",'green', attrs=['bold'])+'...')
                    os.system('brew install httpd')
                    print('Installing '+colored("PHP",'green', attrs=['bold'])+'...')
                    os.system('brew install php')
                    self.vars['apache']='brew'
                else:
                    self.vars['apache']='other'
            
            # set up Apache
            with open('/usr/local/etc/httpd/httpd.conf','r') as f:
                if not 'Include '+self.homedir+'/.config/avalet/httpd/*.conf' in f.read():
                    f.close()
                    f = open('/usr/local/etc/httpd/httpd.conf','a')
                    f.write("""LoadModule php7_module /usr/local/opt/php/lib/httpd/modules/libphp7.so
                    <FilesMatch \.php$>
                       SetHandler application/x-httpd-php
                    </FilesMatch>
                    """)
                    f.write('Include '+self.homedir+'/.config/avalet/httpd/*.conf')
            f.close()
            f = open (self.homedir+'/.config/avalet/httpd/avalet.conf','w+')
            f.write ("""Listen 80
    Listen 443""")
            f.close()
            
            if not Path.is_file(Path(self.homedir+'/.config/avalet/vars')):
                Path(self.homedir+'/.config/avalet/vars').touch(0o644)
                self.updateVars()
            if not Path.is_file(Path(self.homedir+'/.config/avalet/dnsmasq.conf')):
                Path(self.homedir+'/.config/avalet/dnsmasq.conf').touch(0o644)

            # stop Apache and Dnsmasq in order to run on boot instead of login
            # to prevent system load order issues
            print ("""
            Stopping Apache and Dnsmasq""")
            if self.vars['apache']=='brew':
                os.system('sudo brew services stop httpd &>/dev/null')
                os.system('brew services stop httpd &>/dev/null')
            else: 
                os.system('sudo apachectl start &>/dev/null')
            os.system('sudo brew services stop dnsmasq &>/dev/null')
            os.system('brew services stop dnsmasq &>/dev/null')

            # finish  with default tld set up
            self.updateTLD(self.vars['tld'])
        else:
            print ('Avalet already installed. Please run '+colored("avalet reinstall",'green', attrs=['bold']))

    def reinstall(self):
        if self.checkinstall():
            self.uninstall()
        else:
            print ("""Avalet not instaled. Installing...
                """)
        self.install()

    def uninstall(self):
        if self.checkinstall():
            if not ('apache' in self.vars) or self.vars['apache']=='brew':
                print ("""Uninstalling Apache
                """)
                os.system('brew uninstall httpd &>/dev/null')
                os.system('sudo rm -f /usr/local/opt/httpd')
                os.system('sudo rm -f /usr/local/var/homebrew/linked/httpd')
                os.system('sudo rm -rf /usr/local/Cellar/httpd/')
            print ("""Uninstalling Dnsmasq
            """)
            os.system('brew uninstall dnsmasq &>/dev/null')
            os.system('sudo rm -f /usr/local/opt/dnsmasq')
            os.system('sudo rm -f /usr/local/var/homebrew/linked/dnsmasq')
            os.system('sudo rm -rf /usr/local/Cellar/dnsmasq/')
            os.system('sudo rm -rf ~/.config/avalet')

    def updateVars(self):
        with open(self.homedir+'/.config/avalet/vars','wb') as f:
            pickle.dump(self.vars,f)

    def loadVars(self):
        with open(self.homedir+'/.config/avalet/vars','rb') as f:
            self.vars=pickle.load(f)
            
    def list(self):
        print("""Current domains:
        """)
        for i in self.vars['domains']:
            domain = str(i)
            print (domain+self.vars['tld']+"     "+self.vars['domains'][domain]['path'])

# Changes current tld domain
    def updateTLD(self,name):
        self.checkinstall()
        if name[0]!='.':
            name='.'+name
        self.vars['tld'] = name
        self.updateVars()
        os.system('sudo unlink /etc/resolver/'+name[1:])
        os.system('echo "nameserver 127.0.0.1" | sudo tee -a /etc/resolver/'+name[1:])
        f = open (self.homedir+'/.config/avalet/dnsmasq.conf','w+')
        f.write ("address=/"+name[1:]+"""/127.0.0.1
listen-address=127.0.0.1""")
        f.close()
        self.restart()

    def link(self, domain):
        self.checkinstall()
        dirpath = os.getcwd()
        if not domain in self.vars['domains']:
        
            tld = self.vars['tld']
            
            config_dir = self.homedir+'/.config/avalet/'

            vhost="""<VirtualHost {name}{tld}:80>
    ServerName {name}{tld}
    DocumentRoot "{docroot}"
    ErrorLog "{log_dir}/{name}_error_log"
    CustomLog "{log_dir}/{name}_access_log" common
</VirtualHost>
<Directory "{docroot}">
    Options FollowSymLinks Indexes MultiViews
    DirectoryIndex index.php index.html
    AllowOverride All
    Require all granted
</Directory>

            """.format_map({'name':domain,'docroot':dirpath,'dir':config_dir+'certificates/','log_dir':config_dir+'logs','tld':tld})
            file=config_dir+'httpd/'+domain+self.vars['tld']+'.conf'
            print (colored("Domain "+domain+self.vars['tld']+" created at "+dirpath,attrs=['bold']))
            f = open (file, 'w+')
            f.write(vhost)
            f.close()
            #avalet.vars['domains'].append(domain)
            self.vars['domains'][domain]={'secure':False,'path':dirpath,'installed':True}
            self.updateVars()
            self.restart('apache')

    def unlink(self,domain):
        if self.vars['domains'][domain]['secure']:
            print ("""Deletting certificate...
            """)
            certPath = self.config_dir+'/certificates/'+domain+self.vars['tld']
            keyPath = Path(certPath+'.key')
            if (keyPath.exists()):
                keyPath.unlink()
            certPath = Path(certPath+'.crt')
            if (certPath.exists()):
                certPath.unlink()
        print ("""Deletting Apache config...
        """)
        confPath = Path(self.config_dir+'/httpd/'+domain+self.vars['tld']+'.conf')
        if (confPath.exists()):
            confPath.unlink()
        del self.vars['domains'][domain]
        self.updateVars()
        self.restart('apache')

    def secure(self,domain):
        if self.vars['domains'][domain]['secure']:
            print ('Domain '+colored(domain+self.vars['tld'],'green',attrs=['bold'])+' already secured. If you have any problems try to unlink and link again')
        else:
            print ("""Generating certificate...
            """)
            dirpath = os.getcwd()
            config_dir = self.homedir+'/.config/avalet/'
            vhost="""<VirtualHost {name}{tld}:443>
    ServerName {name}{tld}
    DocumentRoot "{docroot}"
    SSLEngine on
    SSLCertificateFile "{dir}{name}{tld}.crt"
    SSLCertificateKeyFile "{dir}{name}{tld}.key"
    ErrorLog "{log_dir}/{name}_error_log"
    CustomLog "{log_dir}/{name}_access_log" common
</VirtualHost>""".format_map({'name':domain,'docroot':dirpath,'log_dir':config_dir+'logs','dir':config_dir+'certificates/','tld':self.vars['tld']})
            cert="""openssl req  -nodes -new -x509  -keyout {dir}{name}{tld}.key -out {dir}{name}{tld}.crt"""
            os.system(cert.format_map({'name':domain,'dir':self.config_dir+'certificates/','tld':self.vars['tld']}))
            file=config_dir+'httpd/'+domain+self.vars['tld']+'.conf'
            f = open (file, 'a')
            f.write(vhost)
            f.close()
            self.vars['domains'][domain]['secure']=True
            self.updateVars()
            self.restart('apache')

    def getDomain(self):
        try:
            sys.argv[2]
        except IndexError:
            dirpath = os.getcwd()
            for i in self.vars['domains']:
                if self.vars['domains'][i]['path']==dirpath:
                    domain = str(i)
                else:
                    domain = os.path.basename(dirpath)
        else:
            domain = sys.argv[2]
        return unidecode(domain.replace(self.vars['tld'],'')).replace(' ','-').lower()
    
    def stop(self):
        print ("""Stopping Apache...
        """)
        if self.vars['apache']=='brew':
            os.system('sudo brew services stop httpd')
        else:
            os.system('sudo apachectl stop')
        print ("""Stopping Dnsmasq...
        """)
        os.system('sudo brew services stop dnsmasq')

    def start(self):
        print ("""Starting Apache...
        """)
        if self.vars['apache']=='brew':
            os.system('sudo brew services start httpd')
        else:
            os.system('sudo apachectl start')
        print ("""Starting Dnsmasq...
        """)
        os.system('sudo brew services start dnsmasq')

    def restart(self,which='all'):
        if which=='all' or which=='apache':
            print ("""Restarting Apache...
        """)
            if self.vars['apache']=='brew':
                os.system('sudo brew services restart httpd &>/dev/null')
            else:
                os.system('sudo apachectl restart')
        if which=='all' or which=='dnsmasq':
            print ("""Restarting Dnsmasq...
        """)
            os.system('sudo brew services restart dnsmasq &>/dev/null')