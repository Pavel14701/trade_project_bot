import asyncio
from abc import ABC
from dataclasses import asdict

from account_events.src.application.dto import WebSocketDTO
from account_events.src.application.interfaces import (
    IConfigEncryption,
    IConnectionStorage,
    IOkxAccountListner,
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
            config_dm = WebSocketDM(**asdict(config))
            encrypted_config_dm = await self._security_gateway.decrypt(
                model=config_dm
            )
            await self._storage_gateway.store_connection(
                config=config_dm
            )
            await self._listner_gateway.connect(
                config=encrypted_config_dm
            )
            return True
        except Exception:
            return False


class AccountEventsUpdaterInteractor(BaseInteractor):
    async def __call__(self, config: WebSocketDTO) -> bool:
        new_config_dm = WebSocketDM(**asdict(config))
        try:
            config_dm: WebSocketDM | None = await self._storage_gateway.get_connection(
                user_id=new_config_dm.user_id
            )
            if config_dm:
                encrypted_config_dm = await self._security_gateway.encrypt(
                    model=new_config_dm
                )
                await self._storage_gateway.store_connection(
                    config=new_config_dm
                )
                await self._listner_gateway.update_subscriptions(
                    config=encrypted_config_dm
                )
            return True
        except Exception:
            return False


class AccountEventsDeleterInteractor(BaseInteractor):
    async def __call__(self, user_id: int) -> bool:
        config_dm = await self._storage_gateway.get_connection(user_id=user_id)
        if config_dm:
            encrypted_config_dm = await self._security_gateway.encrypt(
                model=config_dm
            )
            await self._listner_gateway.close_connection(
                config=encrypted_config_dm
            )
            await self._storage_gateway.remove_connection(
                user_id=user_id
            )
            return True
        return False


class WebSocketRecoveryInteractor(BaseInteractor):
    async def __call__(self) -> None:
        while True:
            await asyncio.sleep(delay=10)
            for user_id in await self._storage_gateway.get_active_connections():
                if config := await self._storage_gateway.get_connection(
                    user_id=user_id
                ):
                    ws_config = WebSocketDM(**asdict(config))
                    encrypted_config = await self._security_gateway.encrypt(
                        model=ws_config
                    )
                    await self._listner_gateway.connect(encrypted_config)


class WebSocketBootstrapInteractor(BaseInteractor):
    async def __call__(self) -> None:
        await asyncio.sleep(delay=2)
        for user_id in await self._storage_gateway.get_active_connections():
            if config := await self._storage_gateway.get_connection(
                user_id=user_id
            ):
                encrypted_config = await self._security_gateway.encrypt(
                        model=config
                    )
                await self._listner_gateway.connect(
                    config=encrypted_config
                )