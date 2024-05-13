import base64

import requests
from rich.console import Console

TIMEOUT_IN_SECONDS = 10

class DeleteFriends:
    def __init__(self) -> None:
        # https://github.com/MixV2/EpicResearch/blob/master/docs/auth/auth_clients.md
        self.client = base64.b64encode(
            b"98f7e42c2e3a4f86a74eb43fbb41ed39:0a2449a2-001a-451e-afec-3e812901c4d7",
        ).decode(
            "utf-8",
        )

        self.console = Console()

        token = self.create_token()
        self.auth_link, self.device_code = self.device_code(token)

    def run(self) -> bool:
        self.console.clear()
        self.console.print("[yellow bold]Epic Games Store Friends Remover")

        self.console.input(
            f"[green bold]Verify login [/green bold][yellow](click enter to continue)[/yellow][green bold]:[/green bold] [red]{self.auth_link}",
        )
        data = self.device_code_verify(self.device_code)

        if not data["success"]:
            self.console.print(f"[red][bold][ERROR][/bold] {data['error_message']}")
            return False

        self.data = data

        self.console.print(f"[green]Successfully logged in [bold]{self.data['display_name']}")

        self.console.print("[green]Removing Friends...")

        friends_count = self.get_friend_count()
        self.delete_friends()

        self.console.print(
            f"[green bold]Removed {friends_count} friends![/green bold] [yellow]You can kill all sessions to reset token.",
        )

        self.console.input()

        return None

    # Reference: https://github.com/MixV2/EpicResearch/blob/master/docs/auth/grant_types/client_credentials.md
    def create_token(self) -> str:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic {self.client}",
        }
        body = {
            "grant_type": "client_credentials",
        }

        data = requests.post(
            "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers=headers,
            data=body,
            timeout=TIMEOUT_IN_SECONDS,
        ).json()

        return data["access_token"]

    # Reference: https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/AccountService/Authentication/DeviceCode/Create.md
    def device_code(self, token) -> tuple:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {token}",
        }

        data = requests.post(
            "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization",
            headers=headers,
            timeout=TIMEOUT_IN_SECONDS,
        ).json()

        return data["verification_uri_complete"], data["device_code"]

    # Reference: https://github.com/MixV2/EpicResearch/blob/master/docs/auth/grant_types/device_code.md
    def device_code_verify(self, device_code) -> dict:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic {self.client}",
        }

        body = {
            "grant_type": "device_code",
            "device_code": device_code,
        }

        data = requests.post(
            "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers=headers,
            data=body,
            timeout=TIMEOUT_IN_SECONDS,
        ).json()

        if "errorCode" in data:
            return {
                "success": False,
                "error_code": data["errorCode"],
                "error_message": data["errorMessage"],
            }

        return {
            "success": True,
            "display_name": data["displayName"],
            "account_id": data["account_id"],
            "access_token": data["access_token"],
        }

    # Reference: https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/FriendsService/Friends/FriendsList.md
    def get_friend_count(self) -> int:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {self.data['access_token']}",
        }

        data = requests.get(
            f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.data['account_id']}/summary",
            headers=headers,
            timeout=TIMEOUT_IN_SECONDS,
        ).json()

        return len(data["friends"])

    # Reference: https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/FriendsService/Friends/Clear.md
    def delete_friends(self) -> None:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {self.data['access_token']}",
        }

        requests.delete(
            f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.data["account_id"]}/friends",
            headers=headers,
            timeout=TIMEOUT_IN_SECONDS,
        )


if __name__ == "__main__":
    app = DeleteFriends().run()
