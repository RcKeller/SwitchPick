#       SwitchPick for JUNOS
#           Code by Keller, UW-IT NIM
#           Config by Norm, UW-IT NIM
#
#   A program that can automatically create serial connections and configure Juniper switchboards
#   This automates the procedure so that configurations can be loaded without touching the CLI.
#
#       Requirements:
#           @ Python 2
#               * Used because of how byte data types are handled
#           @ Pyserial
#               * In CMD: "pip install pyserial"
#           @ A serial connection to a switchboards
#               * This is built around serial communication
#
#       Functions:
#           @ Credential Management
#               * Credentials are automatically loaded, incl. the encrypted password
#               * Credential management allows you to manually change credentials
#           @ Configure Switchboards
#               * Configuration Types:5
#                   - Priming | general config is loaded automatically onto a switch
#                   - Custom | user-supplied files are loaded onto a switch
#               * Configuration Modes:
#                   - Override | loads .config files with stanza formatting
#                   - Set | Loads .txt files that were copy/pasted and reformats them
#           @ Provisioning
#               * View records of switchboard deployments, incl. name, MAC, IP and Subnet
#               * Clear records as necessary
#           @ Generate Logs
#               * Generates & copies support information to a USB drive (for RMA's) automatically
#           @ Wipe Settings
#               * Wiping Modes:
#                   - Prompt | Clear a switch from a login prompt or while logged in
#                   - Loader | Clear a switch as it is booting up, no credentials required
#           @ Power Options
#               * Options:
#                   - Shutdown | Perform a graceful shutdown
#                   - Reboot | Request a reboot
#
#
#
################################################################################
#                                      Imports / Constants
################################################################################

import serial
import easygui
import sys, os
import time

from Tkinter import *
import tkFileDialog
from tkFileDialog import askopenfilename # Open dialog box

CONSOLE = ''        #Our serial connection will be a global value
USERNAME = ''
PASSWORD = ''
ENCRYPTED_PASSWORD = ''
READ_TIMEOUT = 8

CREDENTIAL_FILE = os.path.join(os.path.dirname(sys.argv[0]), 'data', 'data.txt')
GENERAL_CONFIG = os.path.join(os.path.dirname(sys.argv[0]), 'configs', 'prime.config')
PROVISIONING_LOG = os.path.join(os.path.dirname(sys.argv[0]), 'records', 'NIM_log.csv')


BLACKBOX = True     #Blackbox mode is default, False is used for debugging

################################################################################
#                                      Main Function
################################################################################

def main():
    initializeSerialPort()
    loadCredentials()
    while True:
        try:
            menu()
            choice = option(0, 6)
        
            if choice == 0:     #Exit Script
                sys.exit()
            
            if choice == 1:   #Credentials
                credentials()
            elif choice == 2:   #Configure
                configMenu()
                choice = option(0, 2)
                if choice == 1:     #Primer
                    loadConfig(GENERAL_CONFIG)
                elif choice == 2:   #Custom Config
                    file = fileName()
                    if (file != '') and (file != '.'):
                        loadConfig(file)

            elif choice == 3:   #Provisioning
                logExists = provisioningMenu()
                if (logExists == True):
                    choice = option(0, 2)
                    if (choice == 1):
                        provisioningLog()
                    elif (choice == 2):
                        clearProvisioningLog()
                else:
                    print ('No logs found - creating and clearing a new record')
                    clearProvisioningLog()

            elif choice == 4:   #Gather logs
                    logs()

            elif choice == 5:   #Wipe
                wipeMenu()
                choice = option(0, 2)
                if (choice != 0):
                    wipe(choice)

            elif choice == 6:   #Shutdown
                powerMenu()
                choice = option(0, 2)
                if (choice != 0):
                    powerOptions(choice)
                
        except SystemExit:
            return
        except KeyboardInterrupt:
            print ('Process interupped by keyboard - returning to menu')
            
            
################################################################################
#                                      Menu Functions
################################################################################

def menu():
    print('\n\n')
    print('='*40)
    print('SwitchPick for JUNOS - Beta Version')
    print('\tCode by Keller, UW-IT NIM')
    print('\tConfig by Norm, UW-IT NIM')
    print('-'*40)
    print('USER: ' + USERNAME + '\tPASS: ' + ('*' * len(PASSWORD)) + '\nEncryption Loaded:\t' + str(len(ENCRYPTED_PASSWORD) > 1))
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
    print('-'*40)
    print('Switch Config | Process begins at login prompt')
    print('-'*40)
    print('\t1) Priming Config')
    print('\t2) Custom Config')
    print('='*40)
    return
    
    
def wipeMenu():
    print('-'*40)
    print('Wipe Settings | Clear secured data / configs')
    print('-'*40)
    print('\t1) Wipe w/ login')
    print('\t2) Wipe w/ override loader*')
    print('* = Loader can only run directly after the switch is turned on')
    print('='*40)
    return
    
def provisioningMenu():
    print('-'*40)
    print('Provisioning Logs | Records of switch deployments')
    print('File: ' + PROVISIONING_LOG)
    
    fileExists = False
    try:
        if (os.path.exists(PROVISIONING_LOG) == False):
            print('-'*40)
            raise Exception('File not found, no data to read/clear.')
        else:
            fileExists = True
        print('-'*40)
        print('\t1) Read Logs')
        print('\t2) Clear Logs')
        print('='*40)
    except Exception as reason:
        fileExists = False
            
    return fileExists
    
def powerMenu():
    print('-'*40)
    print('Power Options | Junipers require graceful shutdowns')
    print('-'*40)
    print('\t1) Shutdown (graceful)')
    print('\t2) Reboot JUNOS')
    print('-'*40)
    return

    
def loadCredentials():
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
        PASSWORD = ''
        ENCRYPTED_PASSWORD = ''
    print('-'*40)
    return


    
################################################################################
#                                      Primary Functions
################################################################################
    
def credentials():
    print('-'*40)
    print('Edit Credentials:')
    print('-'*40)
    global USERNAME, PASSWORD
    USERNAME = raw_input('Username: ').rstrip('\n')
    PASSWORD = raw_input('Password: ').rstrip('\n')
    return
    

def loadConfig(configFile):
    print('-'*40)
    print('Loading Config:\n' + configFile)
    print('-'*40)

    print('This is a sample distribution of this program.')
    print('Configuration not available.')

    return    

    
def provisioningLog():
    print('-'*80)
    
    try:
    
        file = open(PROVISIONING_LOG, 'r')
        line = file.readline().rstrip('\n')
        returnLine = ''
        while (line != ''):
            line = line.replace(',', '').split()
            for i in range(0, len(line)):
                # line[i] = line[i].rstrip(',')
                returnLine += ('{:20s}'.format(line[i]))
            print(returnLine)
            returnLine = ''
            line = file.readline()
            print('-'*80)
            
    except Exception as reason:
            returnException(reason)
    
    return
    
def logs():
    print('-'*40)
    print('Log Generator | Copies log files to USB drive')
    print('-'*40)
    
    try:
    
        goToLogin()
        login()
        cli()
        command('}', 'request support information | save /var/tmp/RSI.txt', 'Generating RSI files (2 minutes)', False)
        command('}', 'file archive source /var/log destination /var/tmp/LOGS', 'Generating LOG file (30 seconds)', False)
        command('}', 'start shell', 'Moving to shell mode', False)
        
        #Find a drive, mount it, and ensure it is functional
        print('Searching for Drive...')
        while True:     #Requires a special loop that command() cannot accomodate
            time.sleep(1)
            response = readSerial()
            if ('%' in response):
                CONSOLE.write('mount_msdosfs /dev/da1s1 /mnt' + '\n')
                time.sleep(5)
                response = readSerial()
                if ('not permitted' in response):
                    goToLogin()
                    raise Exception('Fatal Error - insufficient permission, unable to mount drives.')
                elif ('no such' not in response) and ('%' in response):   #There isn't a success message
                    print('Drive mounted to /mnt')
                    break
                else:
                    print('...No drive found. Retrying in 15 seconds...')
                    time.sleep(10)
                CONSOLE.write('\n') #Priming for a new loop
        command('%', 'cp /var/tmp/RSI.txt /mnt', 'Copying RSI files')
        command('%', 'cp /var/tmp/LOGS.tar /mnt', 'Copying LOG files', False)
        time.sleep(5)
        command('%', 'umount /mnt', '\nLogs copied! Unmounting drive /mnt', False)    #umount != unmount
        time.sleep(1)
        print('Logging out for security.')
        goToLogin()
        print('Process complete, console at the login screen.')
    
    except Exception as reason:
            returnException(reason)
    
    return

    
def wipe(choice):
    print('-'*40)
    print('Clean Config Wipe | Retains System Logs')
    print('-'*40)
    
    try:
        
        #Reaching shell, either from login or loader
        if (choice == 1): #Login Screen
            goToLogin()
            login()
        else:             #Not at login, assuming we're booting
            loader()
            CONSOLE.write('boot -s\n')
            print('Booting in single user mode (1 minute)...')
            command('root password recovery', 'recovery', 'Starting password recovery, (4 minutes)...', False)
            command('}', 'start shell', 'Starting Shell...', False)
            
        command('%', 'cd /config', 'Directory: /config')
        command('%', 'rm juniper.conf.gz', '\tRemoving: juniper.conf.gz')
        command('%', 'rm juniper.conf.*.gz', '\tRemoving: juniper.conf.*.gz')
        command('%', 'rm rescue.conf.gz', '\tRemoving: rescue.conf.gz')
        command('%', 'cd /var/run/db', 'Directory: /var/run/db')
        command('%', 'rm juniper.db', '\tRemoving: juniper.db')
        command('%', 'rm juniper.data', '\tRemoving: juniper.data')
        command('%', 'rm juniper.save', '\tRemoving: juniper.save')
        print('Wipe complete!')
        
        print('-'*40 + '\nWipe complete. Reboot?\n' + '-'*40)
        print('\t1) Leave as is')
        print('\t2) Power off (graceful)')
        print('\t3) Full reboot')
        print('-'*40)
        choice = option(0, 3)
        print('-'*40)
        if (choice == 2):
            cli()
            powerOff()
        elif (choice == 3):
            cli()
            reboot()
        else:
            print('Returning to menu.')
        
    except Exception as reason:
            returnException(reason)
    
    return
        

def powerOptions(choice):
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
#                                      Secondary Functions
################################################################################

def loader():
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
    loginPrompt = False
    while loginPrompt != True:
        prompt = readSerial()
        if ('login:' in prompt):
            loginPrompt = True
        elif ('[yes,no]' in prompt):
            CONSOLE.write('yes' + '\n')
            time.sleep(0.2)
        else:
            CONSOLE.write('exit' + '\n')
            time.sleep(0.2)
    return
    
    
def login():
    command('login:', USERNAME, 'Logging in...')
    while True:
        time.sleep(1)
        prompt = readSerial()
        #Note: "Password" & "Local Password" are always the same
        if ('word:' in prompt):         #Executes for both password prompts
            CONSOLE.write(PASSWORD + '\n')
            print('Entered password: ' + ('*' * len(PASSWORD)))
        elif ('login' in prompt):       #Username was refused and re-prompted
            raise Exception('Fatal error - wrong username. Please update your credentials.')
        elif ('incorrect' in prompt):   #Incorrect password
            raise Exception('Fatal error - wrong password. Please update your credentials.')
        elif ('JUNOS' in prompt) or ('%' in prompt):
            print('Logged in as ' + USERNAME + '; ' + ('*' * len(PASSWORD)) + '\n')
            break
    return
    
    
def cli():
    command('%', 'cli', 'Entering CLI...')
    return
    
    
def config():
    while True:
        cli()
        command('}', 'configure', 'Entering config mode...', False)
        time.sleep(15)  #Wait and see if the system or autoupdate terminated config mode.
        if ('unexpectedly closed connection' not in readSerial()):
            print('Config mode enabled.')
            break
        else:
            print('Config mode was closed by JUNOS, attempting to reopen')
    return

    
def goodCommit():
    while True:
        time.sleep(5)
        response = readSerial()
        if ('commit complete' in response):
            return True
        elif ('commit failed' in response):
            if (BLACKBOX != True):
                print('REASON:' + response)
            print('-'*40)
            print('Error: This commit has failed - This will require manual troubleshooting')
            print('-'*40)
            return False
            

def powerOff():
    command('}', 'request system power-off\nyes\n', 'Requested shutdown (2 minutes)...', True, False)
    while True:
        time.sleep(15)
        print('...')
        if ('press any key' in readSerial()):
            print('System shutdown complete.')
            print('It is safe to unplug the Juniper')
            break
    return
            
         
def reboot():         
    command('}', 'request system reboot\nyes\n', 'Rebooting (3-4 minutes)...', True, False)
    while True:
        time.sleep(15)
        print('...')
        if ('login:' in readSerial()):
            print('Reboot complete, reached login prompt')
            break
    return

    
    
################################################################################
#                                      Serial Functions
################################################################################

def initializeSerialPort():
    #Loops until able to connect to serial ports.
    print('-'*40)
    print('Auto-Initializing Serial Port: 9600 8-N-1')
    connected = False
    errorPrinted = False
    serialNumber = 9
    while not connected:
        try:
            global CONSOLE
            CONSOLE = serial.Serial(
                port='COM' + str(serialNumber),
                baudrate=9600,
                parity='N',
                stopbits=1,
                bytesize=8,
                timeout=READ_TIMEOUT
            )
            if CONSOLE.isOpen():
                connected = True
                print('\tConnected: COM' + str(serialNumber))
                print('-'*40)
                break
        except:
            serialNumber -= 1
            if serialNumber < 0:
                if errorPrinted == False:
                    print('\tUnable to connect, please reseat adapaters')
                    print('-'*40)
                serialNumber = 9
                time.sleep(10)  #Loops until a successful connection can be established.
    return
                

def readSerial():
    #Reads and returns all the bytes / characters waiting in the serial buffer.
    dataBytes = CONSOLE.inWaiting()
    if dataBytes:
        return CONSOLE.read(dataBytes)
    else:
        return ''
        
        
def command(condition, command, reaction='', pullPrompt=True, newLine=True):
    while True:
        #Loops until conditions are met.
        if (pullPrompt == True):
            #Press enter every second to try and "pull" output from a switch
            CONSOLE.write('\n')
        time.sleep(1)
        response = readSerial()
        if (BLACKBOX != True): #For debugging
            print(response)
        if (condition in response):
            #Adding newlines to commands is optional, some commands may not need them
            CONSOLE.write(command + ('\n' if newLine else ''))
            print(reaction)
            break
    return
    
    
    
################################################################################
#                                      Tertiary Functions
################################################################################

def option(low, high):
    #Loops until a valid option is received in a specified range - for menu selection
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

    
def fileName():
    #Loops until a valid .txt file is specified
        try:
            while True:
                init = Tk()
                init.withdraw()
                name = askopenfilename()
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
            return ''
    
    
def appendProvisioningLog(name, mac, ip, sub):
    file = open(PROVISIONING_LOG, 'a')
    file.write(name + ', ' + mac + ', ' + ip + ', ' + sub + '\n')
    print('-'*40)
    print('Appended to Provisioning Logs:')
    print('-'*40)
    print('NAME\t| ' + name)
    print('MAC\t| ' + mac)
    print('IP\t| ' + ip)
    print('SUB\t| ' + sub)
    print('-'*40)
    return
    
def clearProvisioningLog():
    file = open(PROVISIONING_LOG, 'w')
    file.write('Switch, MAC, IP, SUB\n')
    print('-'*40)
    print('Provisioning records cleared to default')
    print('-'*40)
    return

    
def returnException(reason):
    print('='*40)
    print(reason)
    print('Returning to Menu - see cause above')
    print('='*40)
    return
    
    
################################################################################
#                                      Function Calls
################################################################################

main()