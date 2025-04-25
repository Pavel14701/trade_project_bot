from abc import ABC
import asyncio

from account_events.src.application.dto import WebSocketDTO
from account_events.src.application.interfaces import (
    IConnectionStorage, 
    IOkxAccountListner,
    IConfigEncryption
)
from account_events.src.domain.entities import WebSocketDM


class BaseInteractor(ABC):
    def __init__(
        self,
        storage_gateway: IConnectionStorage,
        listner_gateway: IOkxAccountListner,
        security_gateway: IConfigEncryption
    ) -> None:
        self._storage_gateway = storage_gateway
        self._listner_gateway = listner_gateway
        self._security_gateway = security_gateway


class AccountEventsSubscriberInteractor(BaseInteractor):
    async def __call__(self, config: WebSocketDTO) -> bool:
        try:
            config_dm = WebSocketDM(**config)
            encrypted_config_dm = await self._security_gateway.decrypt(config_dm)
            await self._storage_gateway.store_connection(config_dm)
            await self._listner_gateway.connect(encrypted_config_dm)
            return True
        except Exception:
            return False


class AccountEventsUpdaterInteractor(BaseInteractor):
    async def __call__(self, config: WebSocketDTO) -> bool:
        new_config_dm = WebSocketDM(**config)
        try:
            config_dm: WebSocketDM | None = await self._storage_gateway.get_connection(
                user_id=new_config_dm.user_id
            )
            if config_dm:
                encrypted_config_dm = await self._security_gateway.encrypt(model=new_config_dm)
                await self._storage_gateway.store_connection(
                    config=new_config_dm
                )
                await self._listner_gateway.update_subscriptions(encrypted_config_dm)
            return True
        except Exception:
            return False


class AccountEventsDeleterInteractor(BaseInteractor):
    async def __call__(self, user_id: int) -> bool:
        try:
            config_dm = await self._storage_gateway.get_connection(user_id=user_id)
            encrypted_config_dm = await self._security_gateway.encrypt(model=config_dm)
            await self._listner_gateway.close_connection(config=encrypted_config_dm)
            await self._storage_gateway.remove_connection(user_id)
            return True
        except Exception:
            return False


class WebSocketRecoveryInteractor(BaseInteractor):
    async def __call__(self) -> None:
        while True:
            await asyncio.sleep(10)
            for user_id in await self._storage_gateway.get_active_connections():
                if config := await self._storage_gateway.get_connection(user_id):
                    ws_config = WebSocketDM(**config)
                    encrypted_config = await self._security_gateway.encrypt(
                        model=ws_config
                    )
                    await self._listner_gateway.connect(encrypted_config)


class WebSocketBootstrapInteractor(BaseInteractor):
    async def __call__(self) -> None:
        await asyncio.sleep(2)
        for user_id in await self._storage_gateway.get_active_connections():
            if config := self._storage_gateway.get_connection(user_id):
                ws_config = WebSocketDM(**config)
                encrypted_config = await self._security_gateway.encrypt(
                        model=ws_config
                    )
                await self._listner_gateway.connect(encrypted_config)