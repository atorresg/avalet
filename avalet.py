import os, sys, pathlib
from classes.Avalet import Avalet
from termcolor import colored, cprint

avalet = Avalet()

if len(sys.argv)==1:

    print("""Must use one of the following parameters:
    """
    +colored("install:           ",attrs=['bold'])+"""installs avalet and dependencies (dnsmasq and httpd)
    """
    +colored("link [domain]:     ",attrs=['bold'])+"""creates a domain with the same name as the actual path basename plus tld or a name given as aditional parameter
    """
    +colored("unlink [domain]:   ",attrs=['bold'])+"""deletes a domain with the same name as the actual path basename plus tld or a name given as aditional parameter
    """
    +colored("tld [name]:        ",attrs=['bold'])+"""changes current tld
    """)

else:

    def updateTLD (name):
        if avalet.vars['tld']!=name:
            avalet.updateTLD(name)

    def secure ():
        domain = avalet.getDomain()
        if domain in avalet.vars['domains'] and avalet.vars['domains'][domain]['secure']==False:
            avalet.secure(domain)

    def link ():
        dirpath = os.getcwd()
        domain = avalet.getDomain()
        if not domain in avalet.vars['domains']:
        
            tld = avalet.vars['tld']
            
            config_dir = avalet.homedir+'/.config/avalet/'

            vhost="""<VirtualHost {name}{tld}:80>
    ServerName {name}{tld}
    DocumentRoot "{docroot}"
    ErrorLog "{log_dir}/{name}_error_log"
    CustomLog "{log_dir}/{name}_access_log" common
</VirtualHost>

            """.format_map({'name':domain,'docroot':dirpath,'dir':config_dir+'certificates/','log_dir':config_dir+'logs','tld':tld})
            file=config_dir+'httpd/'+domain+'.conf'
            print (colored("Domain "+domain+" created at "+dirpath,attrs=['bold']))
            f = open (file, 'w+')
            f.write(vhost)
            f.close()
            #avalet.vars['domains'].append(domain)
            avalet.vars['domains'][domain]={'secure':False,'path':dirpath,'installed':True}
            avalet.updateVars()
            os.system('brew services restart httpd')

    def unlink():
        domain = avalet.getDomain()
        if domain in avalet.vars['domains']:
            avalet.unlink(domain)
        else:
            print ('Domain '+domain+avalet.vars['tld']+' does not exist')

    def install():
        avalet.install()

    def list():
        for i in avalet.vars['domains']:
            domain = str(i)
            print (domain+avalet.vars['tld']+"     "+avalet.vars['domains'][domain]['path'])

    menu = {
        'tld':updateTLD,
        'link':link,
        'unlink':unlink,
        'secure':secure,
        'install':install,
        'list':list
    }
    func = menu.get(sys.argv[1])
    func()
