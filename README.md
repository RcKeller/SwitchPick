# SwitchPick for JUNOS
---

A Python software package that can automatically crack, wipe, configure, gather data and record deployments for any Juniper EX network switchboard using a physical connection.

##### Requires:
 - Python 2.7
 - pyserial(any)
 - A physical serial connection to a Juniper switch

 
This program started as a way for me (Keller, UW-IT NIM) to automate my job (network engineering, clearing and loading base configurations onto switches) and has evolved into a solution for what you could call "one-touch" provisioning - loading a config file on a switch prior to deployment with a click of a button.
Or, in this distribution, two keystrokes. The advantage of this program is it allows us to configure switches without a high-level understanding of what is being done, making it possible to delegate and semi-automate complex tasks.
At its core, the implication of this program is a complete separation of the physical and logical work behind network engineering - a cable technician can provision and deploy a switch, and a network engineer can then SSH and perform all configuration remotely.

This works really well loaded onto a raspberry pi with a small touchscreen.


##### Functions:
1. Credential Management
    - Credentials are automatically loaded, incl. the encrypted password
    - Credential management allows you to manually change credentials
2. Configure Switchboards
    - Configuration Types:
        * Priming | general config is loaded automatically onto a switch
        * Custom | user-supplied files are loaded onto a switch
    - Configuration Modes:
        * Override | loads .config files with stanza formatting
        * Set | Loads .txt files that were copy/pasted and reformats them
3. Provisioning
    - View records of switchboard deployments, incl. name, MAC, IP and Subnet
    - Clear records as necessary
4. Generate Logs
    - Generates & copies support information to a USB drive (for RMA's) automatically
5. Wipe Settings
    - Wiping Modes:
        * Prompt | Clear a switch from a login prompt or while logged in
        * Loader | Clear a switch as it is booting up, no credentials required
6. Power Options
    - Options:
        * Shutdown | Perform a graceful shutdown
        * Reboot | Request a reboot