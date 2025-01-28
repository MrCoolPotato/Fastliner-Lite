from nio import AsyncClient, LoginResponse

import asyncio

from CONFIG.env import HOMESERVER


class MatrixClient:
    def __init__(self, signals, main_window):
        self.homeserver = HOMESERVER
        self.client = AsyncClient(self.homeserver)
        self.signals = signals
        self.main_window = main_window

    async def login(self, username, password):
      
        try:
            response = await self.client.login(username, password)
            print(f"Raw response: {response}")
            if isinstance(response, LoginResponse):
                self.client.user_id = response.user_id
                self.client.access_token = response.access_token
                self.signals.messageSignal.emit(
                    f"Login successful as {self.client.user_id}.", "success"
                )
                return True
            else:
                self.signals.messageSignal.emit(
                    f"Login failed: {response.message}", "error"
                )
                return False
        except Exception as e:
            self.signals.messageSignal.emit(f"Login error: {str(e)}", "error")
            return False

    async def start_sync(self):
        
        try:
            self.signals.messageSignal.emit("Starting sync with the homeserver...", "system")
            await self.client.sync_forever(timeout=30000, full_state=True)
        except Exception as e:
            self.signals.messageSignal.emit(f"Sync error: {str(e)}", "error")

    async def login_and_sync(self, username, password):
     
        logged_in = await self.login(username, password)
        if logged_in:
            await self.start_sync()

    async def stop(self):

        await self.client.close()