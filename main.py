import time
import requests
from rich.console import Console
from rich.progress import track

class DeleteFriends:
    def __init__(self):
        self.console = Console()

        self.console.clear()

        self.console.print("[bold yellow]Epic Games Store Friends Remover")
        authorization_code = self.console.input("[green]Please enter your [bold red][link=https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code]Authorization Code[/link]: ")

        self.console.print("[yellow]Creating Access Token...")

        account_data = self.createToken(authorization_code)

        if 0 in account_data and account_data[0] is False:
            self.console.print(f"[red][bold][ERROR][/bold] {account_data[2]}")
            exit()

        self.data = account_data

    def run(self):
        self.console.clear()

        self.console.print(f"[green]Successfully logged in {self.data['displayName']}")

        friends_account_id = self.getFriendsIds()

        for friend_account_id in track(friends_account_id, description="[green]Deleting Friends..."):
            self.deleteFriend(friend_account_id)

            # print(self.accountIdInfo(friend_account_id))

        self.console.print("[green]Done! [yellow]You can kill all sessions to reset token.")

    def createToken(self, authorization_code):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ=",
        }
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code
        }

        response = requests.post("https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token", headers=headers, data=data)

        data = response.json()

        if "errorCode" in data:
            return False, data['errorCode'], data['errorMessage']
        
        account_data = {
            "access_token": data['access_token'],
            "account_id": data['account_id'],
            "displayName": data['displayName'],
            "expires_in": data['expires_in'],
            "expires_at": data['expires_at']
        }
        return account_data

    def getFriendsIds(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {self.data['access_token']}",
        }

        data = requests.get(f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.data['account_id']}/summary", headers=headers).json()
        
        friends_account_id = [friend['accountId'] for friend in data['friends']]
        
        return friends_account_id
    
    def accountIdInfo(self, friend_id):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"bearer {self.data['access_token']}",
        }

        data = requests.get(f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{friend_id}", headers=headers).json()
        
        return data['displayName'], data['id']

    def deleteFriend(self, friend_id):
        while True:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"bearer {self.data['access_token']}",
            }

            response = requests.delete(f"https://friends-public-service-prod.ol.epicgames.com/friends/api/v1/{self.data['account_id']}/friends/{friend_id}", headers=headers)

            data = response.json()

            try:
                if "errorCode" in data:
                    # self.console.print("[yellow] Waiting 20 seconds...")
                    time.sleep(20)
            except requests.exceptions.JSONDecodeError:
                break

        return True
    
if __name__ == "__main__":
    app = DeleteFriends()
    app.run()
