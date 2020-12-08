# Avalet
A script inspired by Laravel's valet but for Apache. It creates Apache .conf files targeting the current path as the DocumentRoot. Only for MacOS

## install
### install Homebrew
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

### install python 3
`brew install python3`  

### install pip
`curl -O https://bootstrap.pypa.io/get-pip.py  
python3 get-pip.py`  

### install Avalet
Execute  
`git clone https://github.com/atorresg/avalet`  
`cd avalet`  
`pip install .`  
If you want to make it global include this on your bash/zsh initialization file  
`alias avalet="python [path]/avalet.py"` where [path] is the path to the folder where you cloned this git  
and after that  
`avalet install`  

## Usage
Just open the terminal and go to any folder which will be the DocumentRoot of the project.

`avalet link example`  
Create the local domain example.test and set the DocumentRoot to the actual path  

`avalet unlink`  
Will delete the domain linked to the actual path  

`avalet secure`  
Create a self signed certificate associated to this domain. From the fields asked when the certificate is created the important one is "Organization Name". After the certificate is generated it will open 'Keychain Access' and you need to open the certificate with the same name as the one you wrote for "Organization Name". You must set "Trust" value to "Trust always" in the first field (the others will update to the same). If you use Chrome when you open that domain with https you must tell Chrome to force load.  

`avalet list`  
Lists all domain an associated paths  

`avalet`  
Will list all commands available  
