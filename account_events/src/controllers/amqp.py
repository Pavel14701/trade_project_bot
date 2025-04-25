from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitRouter

from account_events.src.application.dto import WebSocketDTO
from account_events.src.application.interactors import (
    AccountEventsDeleterInteractor,
    AccountEventsSubscriberInteractor,
    AccountEventsUpdaterInteractor,
    WebSocketBootstrapInteractor,
    WebSocketRecoveryInteractor,
)

controller = RabbitRouter()


class AccountEventsRoutes:
    @controller.subscriber("account_subscriptions_tasks")
    @controller.publisher("account_subscriptions_status")
    @inject
    async def websocket_task(
        self,
        config: dict,
        interactor: FromDishka[AccountEventsSubscriberInteractor],
    ) -> bool:
        """
        Создаёт WebSocket-соединение для пользователя,
        загружая параметры из запроса.
        """
        ws_config = WebSocketDTO(**config)
        return await interactor(ws_config)

    @controller.subscriber("account_update_subscriptions")
    @controller.publisher("account_update_subscriptions_status")
    @inject
    async def update_subscriptions(
        self,
        data: dict,
        interactor: FromDishka[AccountEventsUpdaterInteractor]
    ) -> bool:
        """
        Обновляет подписки пользователя без разрыва соединения.
        """
        ws_config = WebSocketDTO(**data)
        return await interactor(ws_config)

    @controller.subscriber("delete_account_subscriptions")
    @controller.publisher("delete_account_subscriptions_status")
    @inject
    async def close_connection(
        self,
        data: dict,
        interactor: FromDishka[AccountEventsDeleterInteractor]
    ) -> bool:
        user_id = data['user_id']
        return await interactor(user_id)

    @inject
    async def restart_lost_connections(
        self,
        interactor: FromDishka[WebSocketRecoveryInteractor]
    ) -> None:
        """
        Автоматическое восстановление WebSocket при падении соединения.
        """
        await interactor()

    @inject
    async def restore_connections(
        self,
        interactor: FromDishka[WebSocketBootstrapInteractor]
    ) -> None:
        """
        Запускает все сохранённые WebSocket-соединения 
        при перезапуске сервиса.
        """
        await interactor()
