from nio import (
    AsyncClient, 
    LoginResponse, 
    LogoutResponse,
    SyncResponse,
    SyncError,
)

from CONFIG.env import HOMESERVER

import asyncio
import aiohttp


class MatrixClient:
    def __init__(self, signals, main_window):
        self.homeserver = HOMESERVER
        self.client = None
        self.signals = signals
        self.main_window = main_window

        #sync control
        self.running = False
        self.next_batch = None

    async def login(self, username, password):
      
        try:
            self.client = AsyncClient(self.homeserver, username)

            response = await self.client.login(password)
            self.signals.messageSignal.emit(f"Raw response: {response}", "server")
            if isinstance(response, LoginResponse):
                self.client.user_id = response.user_id
                self.client.access_token = response.access_token
                self.signals.messageSignal.emit(
                    f"Login successful as {self.client.user_id}.", "success"
                )
                await self.sync_forever()
                return True
            else:
                self.signals.messageSignal.emit(
                    f"Login failed: {response.message}", "error"
                )
                return False
        except Exception as e:
            self.signals.messageSignal.emit(f"Login error: {str(e)}", "error")
            return False
        
    async def logout(self):

        if not self.client or not self.client.access_token:
            self.signals.messageSignal.emit("You are not logged in.", "warning")
            return False

        try:
            response = await self.client.logout()
            
            if isinstance(response, LogoutResponse):
                self.client.user_id = None
                self.client.access_token = None
                self.signals.messageSignal.emit("Logged out successfully.", "success")
                await self.stop()
                return True
            else:
                self.signals.messageSignal.emit(
                    f"Logout failed: {response.message if hasattr(response, 'message') else 'Unknown error'}",
                    "error",
                )
                return False

        except Exception as e:
            self.signals.messageSignal.emit(f"Logout error: {str(e)}", "error")
            return False    

    async def sync_forever(self):
    
        if not self.client or not self.client.access_token:
            self.signals.messageSignal.emit("Client is not initialized or logged in. Cannot start syncing.", "error")
            return

        self.running = True
        self.signals.messageSignal.emit("Starting batch sync...", "system")

        try:
            while self.running:
                try:
                    response = await self.client.sync(timeout=5000, since=self.next_batch, full_state=False)

                    if isinstance(response, SyncResponse):
                        self.next_batch = response.next_batch

                        await self.process_sync_response(response)

                    elif isinstance(response, SyncError):
                        self.signals.messageSignal.emit(f"Sync error occurred: {response.message}", "error")
                        await asyncio.sleep(5)

                    else:
                        self.signals.messageSignal.emit("Unexpected sync response type.", "error")

                except aiohttp.ClientError as e:

                    self.signals.messageSignal.emit(f"HTTP error during sync: {e}", "error")
                    await asyncio.sleep(5)

                except Exception as e:

                    self.signals.messageSignal.emit(f"Unexpected error during sync: {e}", "error")
                    await asyncio.sleep(5)

        except asyncio.CancelledError:

            self.signals.messageSignal.emit("Sync task was cancelled.", "warning")

        except Exception as e:

            self.signals.messageSignal.emit("Critical error in sync_forever.", "error")

        finally:

            self.running = False


    async def process_sync_response(self, response: SyncResponse):
        
        pass

    async def stop_syncing(self):

        self.signals.messageSignal.emit("Stopping sync process...", "system")
        self.running = False    

    async def stop(self):
        
        await self.stop_syncing()
        await self.client.close()