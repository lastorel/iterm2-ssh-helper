# iterm2-ssh-helper v0.1

Simplify your set of predefined SSH connections for iTerm2 on MacOS like session manager.

Use only one YAML file to define all your "inventory" and  
get your set of iTerm2 Profiles.

Supported system transport:
- SSH2
- SSH1 (to do)
- Telnet (to do)

### devices.yaml example

```YAML
defaults:
  user: bob
  port: 22
  transport: ssh2
  open_pass_manager: true
  extra_args:
groups:
  offices:
    user: ubuntu
  dc1: {}
  core:
    port: 9922
hosts:
  border1:
    ip: 10.14.2.1
    user:
    groups: [core]
  spine2:
    ip: 10.14.15.1
    groups: [core, dc1]
  another-hostname:
    ip: 10.14.15.2
  custom-server:
    ip: 10.14.100.1
    port: 7722
    open_pass_manager: false
    extra_args: -s netconf
    groups: [offices]
```
- `defaults` section defines base low priority rule for each session
- `groups` section defines medium priority rules for child sessions
- `hosts` section defines host name/address and high priority rules

> All generated profiles inherit Default iTerm2 Profile settings.

### Argument reference

- `ip` - address or fqdn to connect
- `user` - username for the session (`ssh username@1.1.1.1`)
- `port`
- `transport` - protocol to use (only `ssh2` supported at the moment)
- `open_pass_manager` - set `true` to automatically open iTerm2 password manager after connect
- `extra_args` - append some extra options to execute in shell

## Installation

1. iTerm2 > Scripts > Manage > Install Python Runtime
2. `~/Library/Application\ Support/iTerm2/iterm2env/versions/*LASTEST_VERSION*/bin/python3 -m pip install pyyaml`
3. `cd ~/Library/Application\ Support/iTerm2/Scripts`
4. `git clone https://github.com/lastorel/iterm2-ssh-helper.git` (or your preferred method)
5. create and compose your inventory file at `~/Documents/devices.yaml`
6. iTerm2 > Scripts > execute new `manager_sync.py`
7. wait a few seconds

> Use `cmd+shift+B` to open Profiles panel
