#!/usr/bin/env python3
import sys
from classes.Avalet import Avalet

avalet = Avalet()

def updateTLD():
    if avalet.vars['tld']!=sys.argv[2]:
        avalet.updateTLD(sys.argv[2])

def link():
    domain = avalet.getDomain()
    if not (domain in avalet.vars['domains']):
        avalet.link(domain)
    else:
        print ('Domain '+domain+avalet.vars['tld']+' already exist. Please first run avalet unlink')

def unlink():
    domain = avalet.getDomain()
    if domain in avalet.vars['domains']:
        avalet.unlink(domain)
    else:
        print ('Domain '+domain+avalet.vars['tld']+' does not exist')

def secure():
    domain = avalet.getDomain()
    if domain in avalet.vars['domains']:
        avalet.secure(domain)
    else:
        print ('Domain '+domain+avalet.vars['tld']+' does not exist')

def start():
    avalet.start()

def stop():
    avalet.stop()

def restart():
    avalet.restart()

def install():
    avalet.install()

def reinstall():
    avalet.reinstall()

def uninstall():
    avalet.uninstall()

def list():
    avalet.list()

def help():
    avalet.help()
    
menu = {
    'tld':updateTLD,
    'link':link,
    'unlink':unlink,
    'secure':secure,
    'install':install,
    'uninstall':uninstall,
    'reinstall':reinstall,
    'stop':stop,
    'start':start,
    'restart':restart,
    'list':list,
    'help':help
}

# if no arguments are passed or not valid, show help
if len(sys.argv)==1 or not (sys.argv[1] in menu):
    avalet.menu()

else:
    func = menu.get(sys.argv[1])
    func()
