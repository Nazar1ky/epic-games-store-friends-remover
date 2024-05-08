import base64

import requests
from rich.console import Console


class DeleteFriends:
    def __init__(self):
        self.client = base64.b64encode(
            "98f7e42c2e3a4f86a74eb43fbb41ed39:0a2449a2-001a-451e-afec-3e812901c4d7"
            .encode("utf-8")
        ).decode("utf-8") # https://github.com/MixV2/EpicResearch/blob/master/docs/auth/auth_clients.md

        self.console = Console()
        self.console.clear()

        self.console.print("[yellow bold]Epic Games Store Friends Remover")

        self.console.print("[yellow]Creating Access Token...")
        token = self.create_token()

        auth_link, device_code = self.device_code(token)

        self.console.input(f"[green bold]Verify login [/green bold][yellow](click enter to continue)[/yellow][green bold]:[/green bold] [red]{auth_link}")
        data = self.device_code_verify(device_code)

        if not data:
            self.console.print("[red][bold][ERROR][/bold] Try restart script.")

        self.data = data

    def run(self):
        self.console.clear()

        self.console.print(f"[green]Successfully logged in {self.data['display_name']}")

        self.console.print("[green]Removing Friends...")

        friends_count = self.get_friend_count()
        self.delete_friends()

        self.console.print(f"[green bold]Removed {friends_count} friends![/green bold] [yellow]You can kill all sessions to reset token.")

    def create_token(self): # Reference: https://github.com/MixV2/EpicResearch/blob/master/docs/auth/grant_types/client_credentials.md
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic {self.client}",
        }
        body = {
            "grant_type": "client_credentials",
        }

        response = requests.post("https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token", headers=headers, data=body)

        data = response.json()

        return data["access_token"]

    def device_code(self, token): # Reference: https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/AccountService/Authentication/DeviceCode/Create.md
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {token}",
        }

        response = requests.post("https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization", headers=headers)

        data = response.json()

        return data["verification_uri_complete"], data["device_code"]

    def device_code_verify(self, device_code): # Reference: https://github.com/MixV2/EpicResearch/blob/master/docs/auth/grant_types/device_code.md
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic {self.client}",
        }

        body = {
            "grant_type": "device_code",
            "device_code": device_code,
        }

        response = requests.post("https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token", headers=headers, data=body)

        data = response.json()

        if "errorCode" in data:
            return None

        return {
            "display_name": data["displayName"],
            "account_id": data["account_id"],
            "access_token": data["access_token"],
        }

    def get_friend_count(self): # Reference: https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/FriendsService/Friends/FriendsList.md
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {self.data['access_token']}",
        }

        data = requests.get(f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.data['account_id']}/summary", headers=headers).json()

        return len(data["friends"])


    def delete_friends(self): # Reference: https://github.com/LeleDerGrasshalmi/FortniteEndpointsDocumentation/blob/main/EpicGames/FriendsService/Friends/Clear.md
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {self.data['access_token']}",
        }

        requests.delete(f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.data["account_id"]}/friends", headers=headers)

if __name__ == "__main__":
    app = DeleteFriends()

    if app.data:
        app.run()
