# SwitchPick
  A program that can automatically create serial connections and configure Juniper switchboards
  This automates the procedure so that configurations can be loaded without touching the CLI.

      Requirements:
          * Python 2
              -Used because of how byte data types are handled
          * Pyserial
              -In CMD: "pip install pyserial"
          * A serial connection to a switchboards
              -This is built around serial communication

      Functions:
          @ Credential Management
              * Credentials are automatically loaded, incl. the encrypted password
              * Credential management allows you to manually change credentials
          @ Configure Switchboards
              * Configuration Types:
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
