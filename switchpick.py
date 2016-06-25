'''
    SwitchPick for JUNOS
        Code by Keller, UW-IT NIM

A program that can automatically create serial connections and configure Juniper switchboards
This automates the procedure so that configurations can be loaded without touching the CLI.

Functions:
  @ Credential Management
      * Credentials are automatically loaded, incl. the encrypted password
      * Credential management allows you to manually change credentials
  @ Configure Switchboards
      * Configuration Types:5
          - Priming | general config is loaded automatically onto a switch
          - Custom | user-supplied files are loaded onto a switch
      * Configuration Modes:
          - Override | loads .config files with stanza formatting
          - Set | Loads .txt files that were copy/pasted and reformats them
  @ Provisioning
      * View records of switchboard deployments, incl. name, MAC, IP and Subnet
      * Clear records as necessary
  @ Generate Logs
      * Generates & copies support information to a USB drive (for RMA's) automatically
  @ Wipe Settings
      * Wiping Modes:
          - Prompt | Clear a switch from a login prompt or while logged in
          - Loader | Clear a switch as it is booting up, no credentials required
  @ Power Options
      * Options:
          - Shutdown | Perform a graceful shutdown
          - Reboot | Request a reboot
'''


################################################################################
#                                      Imports / Constants
################################################################################

import serial
import sys, os
import time

import Tkinter as tk
import tkFileDialog
import tkMessageBox


CONSOLE = ''        #Our serial connection will be a global value
READ_TIMEOUT = 8


USERNAME = ''
PASSWORD = ''
ENCRYPTED_PASSWORD = ''

CREDENTIAL_FILE = os.path.join(os.path.dirname(sys.argv[0]), 'data', 'data.txt')
GENERAL_CONFIG = os.path.join(os.path.dirname(sys.argv[0]), 'configs', 'prime.config')
PROVISIONING_LOG = os.path.join(os.path.dirname(sys.argv[0]), 'records', 'provisioning_log.csv')


################################################################################
#                                      Main Function
################################################################################

def main():
    #Initialize Serial, Load Credentials, and generate a log file if necessary
    initializeSerialPort()
    loadCredentials()
    if (os.path.exists(PROVISIONING_LOG) != True):
        clearProvisioningLog()
    
    #Menu loop
    while True:
        try:
            menu()
            choice = option(0, 6)
        
            #CREDENTIAL MANAGER
            if choice == 1:
                credentials()
            #CONFIG MENU
            elif choice == 2:
                configMenu()
                choice = option(0, 2)
                #PRIMER
                if choice == 1:
                    loadConfig(GENERAL_CONFIG)
                #CUSTOM
                elif choice == 2:
                    file = fileName()
                    if (file != '') and (file != '.'):
                        loadConfig(file)
            #PROVISIONING
            elif choice == 3:
                saveFile(PROVISIONING_LOG)
            #GATHER LOGS
            elif choice == 4:
                    logs()
            #WIPE CONFIGS
            elif choice == 5:
                wipeMenu()
                choice = option(0, 2)
                if (choice != 0):
                    wipe(choice)
            #POWER OPTIONS
            elif choice == 6:
                powerMenu()
                choice = option(0, 2)
                if (choice == 1):
                    powerOff()
                elif (choice == 2):
                    reboot()
            #EXIT SENTINEL
            elif choice == 0:
                sys.exit()

        except KeyboardInterrupt:
            #Pressed Ctrl-C to terminate a subprocess
            print ('\nProcess interupped by keyboard - returning to menu')
            continue
        except SystemExit:
            break
    return
            
            
            
################################################################################
#                                      Initialization
################################################################################

def initializeSerialPort():
    '''Loops until serial communication can be established'''
    print('-'*40)
    print('Auto-Initializing Serial Port: 9600 8-N-1')
    global CONSOLE
    ports = [
        #Windows COM ports
        'COM9', 'COM8', 'COM7',
        'COM6', 'COM5', 'COM4', 
        'COM3', 'COM2', 'COM1',
        #ARM/RPI Port
        '/dev/ttyUSB0',
        #Linux/Unix Ports
        '/dev/ttyS0', '/dev/ttyS1', 
        '/dev/ttyS2', '/dev/ttyS3'
        ]
    index = 0
    errorPrinted = False
    while True:
        try:
            CONSOLE = serial.Serial(
                port=ports[index],
                baudrate=9600,
                parity='N',
                stopbits=1,
                bytesize=8,
                timeout=READ_TIMEOUT
            )
            if CONSOLE.isOpen():
                print('\tConnected: ' + ports[index])
                print(' .'*20)
                break
        except:
            if (index == len(ports) - 1):
                index = 0
                if errorPrinted == False:
                    print('\tUnable to connect, please reseat adapaters')
                    print(' .'*20)
                    errorPrinted == True    #Why print 12x errors?
                    time.sleep(10)  #Loops until a successful connection can be established.
            else:
                index += 1
    return
    
    
def loadCredentials():
    '''Auto-load a credential file, use defaults if unavailable'''
    global USERNAME, PASSWORD, ENCRYPTED_PASSWORD
    try:
        r = open(CREDENTIAL_FILE, 'r')
        credentials = []
        index = 0
        line = r.readline()
        while line != '':
            line = line.rstrip('\n')
            line = line.split()
            if len(line) < 2:
                line.append('')
            credentials.append(line[1])
            index += 1
            line = r.readline()    
        r.close()
        
        print('Auto-Loading credentials:\n' + CREDENTIAL_FILE)
        USERNAME = credentials[0]
        PASSWORD = credentials[1]
        ENCRYPTED_PASSWORD = credentials[2]
        
    except Exception as e:
        print('Could not locate credentials, loading defaults')
        USERNAME = 'root'
        PASSWORD = 'root'
        ENCRYPTED_PASSWORD = ''
    print('-'*40)
    return
    
    
    
################################################################################
#                                      Interfaces
################################################################################

def menu():
    '''Display the main menu'''
    print('\n\n')
    print('='*40)
    print('SwitchPick for JUNOS - Beta v 0.2.8')
    print('\tCode by Keller, UW-IT NIM')
    print(' .'*20)
    print('USER:\t\t' + USERNAME + '\nPASS:\t\t' + ('*' * len(PASSWORD)) + '\nEncryption:\t' + ('Loaded' if str(len(ENCRYPTED_PASSWORD)) > 1 else 'Not loaded'))
    print('='*40)
    print('\t1) Update Credentials')
    print('\t2) Configuration')
    print('\t3) Provisioning')
    print('\t4) Generate Logs')
    print('\t5) Wipe Settings')
    print('\t6) Power Options')
    print('='*40)
    return
    
    
def configMenu():
    '''Displays config options'''
    print('-'*40)
    print('Switch Config | Process begins at login prompt')
    print(' .'*20)
    print('\t1) Priming Config')
    print('\t2) Custom Config')
    print('-'*40)
    return
    

def wipeMenu():
    '''Choose a switch state-of-operation to begin a wipe'''
    print('-'*40)
    print('Wipe Settings | Clear secured data / configs')
    print(' .'*20)
    print('\t1) Wipe w/ login')
    print('\t2) Wipe w/ override loader*')
    print('* = Loader can only run directly after the switch is turned on')
    print('-'*40)
    return
    
    
def powerMenu():
    '''Choose a shutdown option'''
    print('-'*40)
    print('Power Options | Junipers require graceful shutdowns')
    print(' .'*20)
    print('\t1) Shutdown (graceful)')
    print('\t2) Reboot JUNOS')
    print('-'*40)
    return

    

################################################################################
#                                      Primary Operations
################################################################################
    
def credentials():
    '''User prompt to update instance-based credentials'''
    print('-'*40)
    print('Edit User Credentials:')
    print(' .'*20)
    global USERNAME, PASSWORD
    USERNAME = raw_input('Username: ').rstrip('\n')
    PASSWORD = raw_input('Password: ').rstrip('\n')
    print('-'*40)
    return
    

def loadConfig(configFile):
    '''
    Load a config file, formatting as necessary
    Console in, configure and commit encrypted credentials
    Load the config, ensure all commits are successful
    Clone configs to rescue files    
    '''
    print('-'*40)
    print('Loading Config:\n' + configFile)
    print('-'*40)
    
    try:
    
        if (ENCRYPTED_PASSWORD == ''):
            raise Exception('Fatal Error - no encryption password or hash loaded in data.txt')
        '''There are two kinds of config files that go through different processes:
            .config / "Stanza" | Must load with override terminal, no formatting
            .txt / "Excel configs" | Must load with set terminal, program will format before writing'''
        terminalType = 'set' if (configFile[-4:] == '.txt') else 'override'
        
        #Navigate to config, loop until the session is stable
        goToLogin()
        login()
        cli()
        config()

        #Commit a password - first step for security purposes
        command('#', 'load factory-default', '\nLoading Factory Settings...')
        command('#', ('set system root-authentication encrypted-password ' + ENCRYPTED_PASSWORD), '\tSetting Encrypted Root Password...', False)
        command('#', 'commit comment "loading factory-default"', 'Committing Initial Password...', False)
        if goodCommit() != True:
            return
        print('Encrypted login credentials commited.')
            
        #Load a terminal and apply bulk configurations
        command('#', ('load '+terminalType+' terminal'),
            ('\nOpening '+terminalType+' terminal...'))
        r = open(configFile, 'r')
        configData = r.read()
        if (terminalType == 'set'):
            configData = configData.format(r'\r\n\\')   #Format with raw newlines
        try:
            time.sleep(0.2)   #Configs can be 1K lines, interpreter needs a moment to process
            print('\tLoading configs (1 minute)...')
            CONSOLE.write(configData)   #Takes a bit
            time.sleep(0.2)
            print('\tConfigs loaded to terminal.')
        except:
            print('Error: Unable to write config data to console.')
        r.close()
        #Write a raw newline & the hex code for CTRL-D
        command('', '\r\n\x04', 'Closing terminal', True, False)
        time.sleep(1)   #Time MUST pass for this to process
        #Commit and copy config
        command('#', 'commit and-quit', 'Committing loaded configs...', False)
        if goodCommit() != True:
            return
        print('Configuration file loaded without errors.')
        command('}', 'request system configuration rescue save', '\nCloning configs to rescue settings...')
        
        time.sleep(5)   #Let the system grab an available IP
        gatherProvisioningInfo(configFile)
        print('Config complete!')
        powerOff()
    
    except Exception as reason:
        returnException(reason)
    return    
    
    
def logs():
    '''Generate support information, copy to a USB drive connected to a switch'''
    print('-'*40)
    print('Log Generator | Copies log files to USB drive')
    print('-'*40)
    
    try:
    
        goToLogin()
        login()
        cli()
        command('}', 'request support information | save /var/tmp/RSI.txt', 'Generating RSI files (2 minutes)')
        command('}', 'file archive source /var/log destination /var/tmp/LOGS', 'Generating LOG file (30 seconds)', False)
        command('}', 'start shell', 'Moving to shell mode', False)
        
        #Find a drive, mount it, and ensure it is functional
        print('Searching for Drive...')
        '''
        Loops until we can verify the drive was NOT rejected
        There is NO success message and thus we can't guarentee a mount is formatted well
        '''
        while True:
            time.sleep(1)
            response = readSerial()
            if ('%' in response):
                CONSOLE.write('mount_msdosfs /dev/da1s1 /mnt' + '\n')
                time.sleep(5)       #This command takes a few seconds to process
                response = readSerial()
                if ('not permitted' in response):
                    goToLogin()
                    raise Exception('Fatal Error - insufficient permission, unable to mount drives.')
                elif ('no such' not in response) and ('%' in response):
                    print('Drive mounted to /mnt, no errors received from JUNOS')
                    break
                else:
                    print('...No drive found. Retrying in 15 seconds...')
                    time.sleep(10)
                CONSOLE.write('\n') #Priming for a new loop
        command('%', 'cp /var/tmp/RSI.txt /mnt', 'Copying RSI files')
        command('%', 'cp /var/tmp/LOGS.tar /mnt', 'Copying LOG files', False)
        command('%', 'umount /mnt', '\nLogs copied! Unmounting drive /mnt', False)    #umount != unmount
        
        print('Logging out for security.')
        goToLogin()
        print('Process complete, console at the login screen.')
    
    except Exception as reason:
        returnException(reason)
    return

    
def wipe(choice):
    '''Clear a switch without zeroize, thus retaining long-term support/operational data'''
    print('-'*40)
    print('Clean Config Wipe | Retains System Logs')
    print('-'*40)
    
    try:
        
        #Start a shell session
        if (choice == 1): #From login screen
            goToLogin()
            login()
        else:             #Using loader override
            print('Note: This process takes a LONG time (~10 minutes)')
            loader()
            CONSOLE.write('boot -s\n')
            print('Booting in single user mode (1 minute)...')
            command('root password recovery', 'recovery', 'Starting password recovery, (4 minutes)...', False)
            command('}', 'start shell', 'Starting Shell...', False)
            
        command('%', 'cd /config', 'Directory: /config')
        command('%', 'rm juniper.conf.gz', '\tRemoving: juniper.conf.gz')
        command('%', 'rm juniper.conf.*.gz', '\tRemoving: juniper.conf.*.gz')
        command('%', 'rm rescue.conf.gz', '\tRemoving: rescue.conf.gz')
        command('%', 'cd /var/run/db', 'Directory: /var/run/db', False)
        command('%', 'rm juniper.db', '\tRemoving: juniper.db')
        command('%', 'rm juniper.data', '\tRemoving: juniper.data')
        command('%', 'rm juniper.save', '\tRemoving: juniper.save')
        print('Wipe complete!')
        
        print('-'*40 + '\nWipe complete!' + '-'*40)
        reboot()
        
    except Exception as reason:
        returnException(reason)
    return
        

def powerOptions(choice):
    '''Graceful shutdown options for a switch, prevents error/event logging'''
    print('-'*40)
    if (choice == 0):
        print('Returning to menu.')
    else:
        try:
            goToLogin()
            login()
            cli()
            if (choice == 1):
                powerOff()
            elif (choice == 2):
                reboot()
        
        except Exception as reason:
            returnException(reason)
    return
    
    
    
################################################################################
#                                      State Modulators
################################################################################

def loader():
    '''Go to the "loader override" when you turn on a switch'''
    print('Attempting to enter loader...')
    while True:
        time.sleep(1)
        CONSOLE.write(' ')
        prompt = readSerial()
        if ('loader>' in prompt):
            print('Loader initialized.')
            break
        elif ('login:' in prompt):
            print('Reached login screen instead.')
            break
    return

    
def goToLogin():
    '''Exit out of all prompts until the login screen is reached'''
    loginPrompt = False
    while loginPrompt != True:
        prompt = readSerial()
        if ('login:' in prompt):
            loginPrompt = True
        elif ('[yes,no]' in prompt):    #Interrupt any commits
            CONSOLE.write('yes' + '\n')
            time.sleep(0.2)
        else:
            CONSOLE.write('exit' + '\n')
            time.sleep(0.2)
    return
    
    
def login():
    '''Login to a switch, raise an exception if necessary'''
    command('login:', USERNAME, 'Logging in...')
    while True:
        time.sleep(0.5)
        prompt = readSerial()
        #Password and Local Password are always the same, this statement covers both:
        if ('word:' in prompt):
            CONSOLE.write(PASSWORD + '\n')
            print('Entered password: ' + ('*' * len(PASSWORD)))
        elif ('login' in prompt):       #Username was refused and re-prompted
            raise Exception('Fatal error - wrong username. Please update your credentials.')
        elif ('incorrect' in prompt):   #Incorrect password
            raise Exception('Fatal error - wrong password. Please update your credentials.')
        elif ('JUNOS' in prompt) or ('%' in prompt):
            print('Logged in as ' + USERNAME + '; ' + ('*' * len(PASSWORD)) + '\n')
            break
        elif (prompt == ''):
            CONSOLE.write('\n')
    return
    
    
def cli():
    '''Issue commands to enter CLI mode'''
    command('%', 'cli', 'Entering CLI...')
    return
    
    
def config():
    '''
    Enter configuration mode in preparation to commit changes
    Verify mode can be sustained - JUNOS cancels sessions with "Auto-Update"
    40% of the time within the first 5 seconds. Hence why we sleep for 15 seconds.
    '''
    while True:
        command('}', 'configure', 'Entering config mode, verifying stable session...')
        time.sleep(15)  #Wait and see if the system or autoupdate terminated config mode.
        if ('unexpectedly closed connection' not in readSerial()):
            print('Config mode enabled, steady.')
            break
        else:
            print('Config mode was closed by JUNOS, attempting to reopen')
            cli()
    return

    
def goodCommit():
    '''Loops until we have absolute verification that commits were successful'''
    while True:
        time.sleep(5)
        response = readSerial()
        if ('commit complete' in response):
            return True
        elif ('commit failed' in response):
            print('-'*40)
            print('Error: This commit has failed - This will require manual troubleshooting')
            print('-'*40)
            return False
            
            
def gatherProvisioningInfo(configFile):
    '''
    Gathers model/serial/config file/mac/ip/subnet information,
    then passes it to a function to append a spreadsheet
    '''
    #Grab model/serial via chassis hardware
    command('}', 'show chassis hardware | match chassis', '\nReviewing model information...')
    time.sleep(1)
    chassis = readSerial().split()
    model = 'N/A'
    serial = 'N/A'
    try:
        for i in range(len(chassis)):
            if (chassis[i] == 'Chassis'):
                model = chassis[i + 2]
                serial = chassis[i + 1]
    except:
        pass
                
    #Config file name is the base of the filename
    name = os.path.basename(configFile).split('.')[0]
    
    #Grab mac address from current interface
    command('}', 'show interfaces vlan | find Current', 'Checking for MAC address...')
    time.sleep(1)
    current = readSerial().split()
    mac = 'N/A'
    try:
        for i in range(len(current)):
            if (current[i] == 'Current'):
                mac = current[i + 2].rstrip(',')
    except:
        pass
                
    #Grab IP/SUB from interface destinations
    command('}', 'show interfaces vlan | find Destination', 'Checking for IP/SUB...')
    time.sleep(1)
    destination = readSerial().split()
    ip = 'N/A'
    sub = 'N/A'
    try:
        for i in range(len(destination)):
            if (destination[i] == 'Local:'):
                ip = destination[i + 1].rstrip(',')
                sub = destination[i + 3].rstrip(',')
    except:
        pass
        
    #Append all these to a CSV file
    appendProvisioningLog(  model, serial, name, mac, ip, sub)
    return


def powerOff():
    '''Shutdown loop that prints "..." when powering off (so user knows the code has not frozen)'''    
    try:
        root = tk.Tk()
        root.withdraw()
        option = tkMessageBox.askquestion("Shutdown", "Perform a graceful shutdown? (takes 2 minutes)", icon='warning')
        root.destroy()
        if (option != 'yes'):
            return
            
        print('-'*40)
        print('Graceful Shutdown (2-3 minutes)')
        print('-'*40)
        goToLogin()
        login()
        cli()
        command('}', 'request system power-off\nyes\n', 'Requested shutdown (3 minutes)...', True, False)
        while True:
            time.sleep(15)
            print('...')
            if ('press any key' in readSerial()):
                print('System shutdown complete.')
                print('It is safe to unplug the Juniper')
                break
    except Exception as reason:
        returnException(reason)
    return
            
         
def reboot():
    '''Reboot a switch, and wait for it to return to login prompt'''
    try:
        root = tk.Tk()
        root.withdraw()
        option = tkMessageBox.askquestion("Reboot", "Reboot? (takes 4 minutes)", icon='warning')
        root.destroy()
        if (option != 'yes'):
            return
        
        print('-'*40)
        print('Graceful Reboot (4 minutes)')
        print('-'*40)
        goToLogin()
        login()
        cli()
        command('}', 'request system reboot\nyes\n', 'Rebooting (3-4 minutes)...', True, False)
        while True:
            time.sleep(15)
            print('...')
            if ('login:' in readSerial()):
                print('Reboot complete, reached login prompt')
                break
    except Exception as reason:
        returnException(reason)
    return

    
    
################################################################################
#                                      I/O Opetrations
################################################################################
    
def fileName():
    '''
    Open a file browsing prompt using tKinter, user specifies a file
    Return a blank file if user cancels or specifies an invalid file
    '''
    try:
        init = tk.Tk()
        init.withdraw()
        name = tkFileDialog.askopenfilename()
        if (name == '.') or (name == ''):
            raise Exception('No file specified.')
        r = open(name, 'r')
        data = r.read()
        if data == '':
            raise Exception('No data contained in: ' + name)
        r.close()
        return name
    except Exception as reason:
        returnException(reason)
    return


def saveFile(source):
    '''
    Saves a source file to a user specified location.
    '''
    try:
        r = open(source, 'r')
        data = r.read()
        if data == '':
            raise Exception('No data contained in: ' + source)
        r.close()
    
        init = tk.Tk()
        init.withdraw()
        dest = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        if (type(dest) != file):
            raise Exception('No file specified.')
        else:
            dest.write(data)
            dest.close()
            print('File exported successfully!')
        
    except Exception as reason:
        returnException(reason)
    return
    
    
def appendProvisioningLog(model, serial, config, mac, ip, sub):
    '''Add an entry to provisioning logs'''
    file = open(PROVISIONING_LOG, 'a')
    file.write(model + ', ' + serial + ', ' + config + ', ' + mac + ', ' + ip + ', ' + sub + '\n')
    file.close()
    print('-'*40)
    print('Appended to Provisioning Logs:')
    print(' .'*20)
    print('MODEL\t| ' + model)
    print('SERIAL\t| ' + serial)
    print('CONFIG\t| ' + config)
    print('MAC\t| ' + mac)
    print('IP\t| ' + ip)
    print('SUB\t| ' + sub)
    print('-'*40)
    return
    
    
def clearProvisioningLog():
    '''Reset / create a fresh provisioning log'''
    file = open(PROVISIONING_LOG, 'w')
    file.write('Model, Serial, Config, MAC, IP, SUB\n')
    file.close()
    print('-'*40)
    print('Provisioning records cleared to default')
    print('-'*40)
    return
    
    

################################################################################
#                                      Tertiary Operations
################################################################################

def option(low, high):
    '''Loops until valid menu options are selected'''
    while True:
        try:
            option = int(input('Option >    '))
            if (option >= low) and (option <= high):
                break
            else:
                print('Option must be between ' + low + '-' + high)
        except KeyboardInterrupt as reason:
            sys.exit()
        except:
            print('Option not accepted')
    return option

    
def returnException(reason):
    '''Formatting for returning an exception'''
    print('='*40)
    print(reason)
    print('Returning to Menu - see cause above')
    print('='*40)
    return
    
    
    
################################################################################
#                                      Serial Operations
################################################################################

def readSerial():
    '''
    Read and return bytes in the serial buffer. NOTE, there is a physical restriction
    that limits buffer size to around 400-500 chars and losing data in transmission
    is common for these interfaces. To keep reading excess chars to a minimum, we only read the
    same amount as chars in the buffer.
    '''
    dataBytes = CONSOLE.inWaiting()
    if dataBytes:
        return CONSOLE.read(dataBytes)
    else:
        return ''
        
        
def command(condition, command, reaction='', pullPrompt=True, newLine=True):
    '''
    When a condition is passed from the serial device, respond with a command,
    then print a notification to user terminal.
    Optional: "Pull" prompts by pressing enter every second, which prevents
    the program from hanging when JUNOS fails to provide prompts.
    '''
    while True:
        if (pullPrompt == True):
            CONSOLE.write('\n') #Brute-force the console to respond
        time.sleep(1)
        response = readSerial()
        if (condition in response):
            CONSOLE.write(command + ('\n' if newLine else ''))
            print(reaction)
            break
    return
    
    
    
################################################################################
#                                      Function Calls
################################################################################

main()