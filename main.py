import base64

import requests
from rich.console import Console
from rich.prompt import Confirm

TIMEOUT_IN_SECONDS = 10

# CLIENT_ID:SECRET
CLIENT = b"98f7e42c2e3a4f86a74eb43fbb41ed39:0a2449a2-001a-451e-afec-3e812901c4d7"


class FriendsRemover:
    def __init__(self) -> None:
        # https://github.com/MixV2/EpicResearch/blob/master/docs/auth/auth_clients.md
        self.client = base64.b64encode(
            CLIENT,
        ).decode(
            "utf-8",
        )

        self.session = requests.Session()

        self.account_id = None
        self.bearer = None

    def run(self) -> None:
        console = Console()
        console.clear()

        console.print("[yellow bold]Epic Games Store Friends Remover")

        token = self.token()["access_token"]

        device_code = self.device_code(token)

        console.input(
            f"[bold][green]Login (press enter to continue):[/green] [red]{device_code['verification_uri_complete']}",
        )

        try:
            data = self.device_code_verify(device_code["device_code"])
        except requests.HTTPError:
            console.print("[red]User not logged in!")
            return

        self.account_id = data["account_id"]
        self.bearer = data["access_token"]

        console.print(f"[bold][green]Successfully logged in [blue]{data['displayName']}")

        friends = self._get_friends()

        friends_count = len(friends["friends"])

        confirm = Confirm.ask(
            f"[bold][yellow]You have [blue]{friends_count} [yellow]friends! "
            "You sure you want to remove all friends?",
        )

        if confirm:
            self._remove_friends()
            console.print(f"[bold][green]Removed {friends_count} friends!")

        self._kill_session()

        console.print(
            "[bold][yellow]Session has been killed",
        )

        console.input()

    def token(self) -> dict:
        """https://github.com/MixV2/EpicResearch/blob/master/docs/auth/grant_types/client_credentials.md"""
        headers = {"Authorization": f"basic {self.client}"}

        body = {"grant_type": "client_credentials"}

        response = self.session.post(
            "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers=headers,
            data=body,
            timeout=TIMEOUT_IN_SECONDS,
        )

        response.raise_for_status()

        return response.json()

    def device_code(self, token: str) -> dict:
        """https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/AccountService/Authentication/DeviceCode/Create.md"""
        headers = {
            "Authorization": f"bearer {token}",
        }

        response = self.session.post(
            "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/deviceAuthorization",
            headers=headers,
            timeout=TIMEOUT_IN_SECONDS,
        )

        response.raise_for_status()

        return response.json()

    def device_code_verify(self, device_code) -> dict:
        """https://github.com/MixV2/EpicResearch/blob/master/docs/auth/grant_types/device_code.md"""
        headers = {
            "Authorization": f"basic {self.client}",
        }

        body = {
            "grant_type": "device_code",
            "device_code": device_code,
        }

        response = self.session.post(
            "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers=headers,
            data=body,
            timeout=TIMEOUT_IN_SECONDS,
        )

        response.raise_for_status()

        return response.json()

    def _get_friends(self) -> dict:
        """https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/FriendsService/Friends/FriendsList.md"""
        headers = {
            "Authorization": f"bearer {self.bearer}",
        }

        response = self.session.get(
            f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.account_id}/summary",
            headers=headers,
            timeout=TIMEOUT_IN_SECONDS,
        )

        response.raise_for_status()

        return response.json()

    def _remove_friends(self) -> None:
        """https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/FriendsService/Friends/ClearFriendsList.md"""
        headers = {
            "Authorization": f"bearer {self.bearer}",
        }

        self.session.delete(
            f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.account_id}/friends",
            headers=headers,
            timeout=TIMEOUT_IN_SECONDS,
        )

    def _kill_session(self) -> None:
        """https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/AccountService/Authentication/Kill/Session.md"""
        headers = {
            "Authorization": f"bearer {self.bearer}",
        }

        self.session.delete(
            f"https://account-public-service-prod.ol.epicgames.com/account/api/oauth/sessions/kill/{self.bearer}",
            headers=headers,
            timeout=TIMEOUT_IN_SECONDS,
        )

def main() -> None:
    friends_remover = FriendsRemover()
    friends_remover.run()

if __name__ == "__main__":
    main()
