# SwitchPick
Python 2 | Requires: pyserial, serial connection
Automatically configure, deploy, and track Juniper switchboard installations
Using serial communication, the program interfaces with equipment in the absence of any offline API or a dependable communication standard.

Features:
  *Automatically establishes a serial connection
  *Load credentials and encryption keys automatically or manually
  *Configure switchboards with a "priming" configuration, allowing them to be SSH'd into once deployed.
  *Load custom configs of multiple standards ('.txt' and '.config'), and modify file contents & algorithms as necessary.
  *Generate support information and automatically copy it to a flash drive.
  *Clear a switchboard without zeroize, preventing loss of support information.
  *Graceful shutdown and reboot functions.
