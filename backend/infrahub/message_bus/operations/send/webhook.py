import json
from typing import Dict, Type

from infrahub.message_bus import messages
from infrahub.services import InfrahubServices
from infrahub.webhook import CustomWebhook, StandardWebhook, TransformWebhook, Webhook


async def event(message: messages.SendWebhookEvent, service: InfrahubServices) -> None:
    webhook_definition = await service.cache.get(key=f"webhook:active:{message.webhook_id}")
    if not webhook_definition:
        service.log.warning("Webhook not found", webhook_id=message.webhook_id)
        return

    webhook_data = json.loads(webhook_definition)
    payload = {"event_type": message.event_type, "data": message.event_data, "service": service}
    webhook_map: Dict[str, Type[Webhook]] = {
        "standard": StandardWebhook,
        "custom": CustomWebhook,
        "transform": TransformWebhook,
    }
    webhook_class = webhook_map[webhook_data["webhook_type"]]
    payload.update(webhook_data["webhook_configuration"])
    webhook = webhook_class(**payload)
    await webhook.send()