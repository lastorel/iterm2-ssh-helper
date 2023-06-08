import json
import subprocess
import yaml
from pathlib import Path
from typing import Optional, Union, List

import iterm2


INVENTORY_FILE = f"{Path.home()}/Documents/devices.yaml"


def generate_guid() -> str:
    r = subprocess.run("uuidgen", capture_output=True, encoding="utf-8")
    return r.stdout.strip()


def get_inventory() -> dict:
    filename = INVENTORY_FILE
    with open(filename) as f:
        data = yaml.safe_load(f)
    return data


def generate_command(command: str, user: Optional[str], ip: str, port: Optional[str], extra_args: Optional[str]) -> str:
    command = f"{command} "
    if user:
        command += f"{user}@"
    command += ip
    if port:
        command += f" -p {port}"
    if extra_args:
        command += f" {extra_args}"
    return command


def get_profiles() -> list:
    data = {}
    if not Path(f"{Path.home()}/Library/Application Support/iTerm2/DynamicProfiles/Profiles.json").exists():
        clean_pls = True
    else:
        clean_pls = False
    if not clean_pls:
        with open(f"{Path.home()}/Library/Application Support/iTerm2/DynamicProfiles/Profiles.json") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                clean_pls = True
            if "Profiles" not in data:
                clean_pls = True
    if clean_pls:
        with open(f"{Path.home()}/Library/Application Support/iTerm2/DynamicProfiles/Profiles.json", "w") as f:
            json.dump({"Profiles": []}, f)
    return None if clean_pls else data["Profiles"]


class Profile(object):
    transport_map = {
        None: "ssh",
        "ssh2": "ssh",
    }

    def __init__(self, hostname: str, host_data: dict, defaults: Optional[dict], groups: Optional[dict]):
        # mandatory arguments
        self.hostname = hostname
        self.ip: str = host_data["ip"]

        # options
        self.user: Optional[str] = None
        self.port: Optional[Union[int, str]] = None
        self.transport: Optional[str] = None
        self.open_pass_manager: Optional[bool] = None
        self.extra_args: Optional[str] = None

        self.tags = []
        self.is_parent = False
        self.guid = None

        if defaults:
            self.user = defaults.get("user")
            self.port = defaults.get("port")
            self.transport = defaults.get("transport")
            self.open_pass_manager = defaults.get("open_pass_manager")
            self.extra_args = defaults.get("extra_args")

        if host_data.get("groups"):
            for group in host_data["groups"]:
                if groups and group in groups:
                    self.user = groups[group]["user"] if "user" in groups[group] else self.user
                    self.port = groups[group]["port"] if "port" in groups[group] else self.port
                    self.transport = groups[group]["transport"] if "transport" in groups[group] else self.transport
                    self.open_pass_manager = (
                        groups[group]["open_pass_manager"]
                        if "open_pass_manager" in groups[group] else self.open_pass_manager
                    )
                    self.extra_args = groups[group]["extra_args"] if "extra_args" in groups[group] else self.extra_args
                    self.tags.append(group)

        self.user = host_data["user"] if "user" in host_data else self.user
        self.port = host_data["port"] if "port" in host_data else self.port
        self.transport = host_data["transport"] if "transport" in host_data else self.transport
        self.open_pass_manager = (
            host_data["open_pass_manager"] if "open_pass_manager" in host_data else self.open_pass_manager
        )
        self.extra_args = host_data["extra_args"] if "extra_args" in host_data else self.extra_args

    def generate_guid(self) -> None:
        self.guid = generate_guid()

    def json(self) -> dict:
        data = {
            "Title Components": 34,
            "Name": self.hostname,
            "Custom Command": "Yes",
        }
        if self.guid:
            data["Guid"] = self.guid
        if self.tags:
            data["Tags"] = self.tags
        if self.open_pass_manager is not None:
            data["Open Password Manager Automatically"] = self.open_pass_manager
        data["Command"] = generate_command(
            command=self.transport_map[self.transport],
            user=self.user,
            ip=self.ip,
            port=self.port,
            extra_args=self.extra_args,
        )

        return data


def dump_profiles(profiles: List[Profile]) -> None:
    with open(f"{Path.home()}/Library/Application Support/iTerm2/DynamicProfiles/Profiles.json", "w") as f:
        json.dump({"Profiles": [p.json() for p in profiles]}, f, indent=2)


async def main(connection):
    try:
        inventory = get_inventory()
        if "hosts" not in inventory or not inventory:
            raise ValueError("Inventory can not be empty")
    except Exception as exc:
        alert = iterm2.alert.Alert(title="Error", subtitle=str(exc))
        await alert.async_run(connection)
        return

    profiles = []
    for hostname, host_data in inventory["hosts"].items():
        profile = Profile(
            hostname=hostname, host_data=host_data, defaults=inventory.get("defaults"), groups=inventory.get("groups")
        )
        profiles.append(profile)

    created_profiles = get_profiles()
    if created_profiles:
        for profile in profiles:
            for c_profile in created_profiles:
                if profile.hostname == c_profile["Name"]:
                    profile.guid = c_profile["Guid"]
                    break
    for profile in profiles:
        if not profile.guid:
            profile.generate_guid()

    dump_profiles(profiles)


iterm2.run_until_complete(main)
