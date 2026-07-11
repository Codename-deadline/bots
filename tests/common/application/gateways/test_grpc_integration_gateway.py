from common.application.enums import Language, Messenger
from common.application.gateways.grpc_integration_gateway import GrpcIntegrationGateway
from common.application.protocols.integration_gateway import ScopeType
from common.infrastructure.grpc.generated import integration_pb2

BOT_ID: int = 42


class RecordingIntegrationService:
    def __init__(self):
        self.calls = []

    async def SubscribeToOrganization(self, request, **kwargs):
        self.calls.append(("SubscribeToOrganization", request))
        return self._response()

    async def UnsubscribeFromThread(self, request, **kwargs):
        self.calls.append(("UnsubscribeFromThread", request))
        return self._response()

    async def LinkMessengerAccount(self, request, **kwargs):
        self.calls.append(("LinkMessengerAccount", request))
        return self._response()

    async def RegisterChat(self, request, **kwargs):
        self.calls.append(("RegisterChat", request))
        return self._response()

    async def DeregisterChat(self, request, **kwargs):
        self.calls.append(("DeregisterChat", request))
        return self._response()

    def _response(self):
        return integration_pb2.GeneralResponse(
            key="register_chat.success", locale=integration_pb2.EN
        )


def _gateway(service: RecordingIntegrationService) -> GrpcIntegrationGateway:
    gateway = GrpcIntegrationGateway("localhost:0", Messenger.TELEGRAM, bot_id=BOT_ID)
    gateway._integration_service = service  # pyright: ignore[reportAttributeAccessIssue]
    return gateway


async def test_subscribe_to_scope_maps_to_correct_rpc_and_fields():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.subscribe_to_scope(ScopeType.ORGANIZATION, 10, 20, 30, True)

    name, request = service.calls[0]
    assert name == "SubscribeToOrganization"
    assert request.issuer_messenger_account_id == 10
    assert request.target_id == 20
    assert request.messenger_chat_id == 30
    assert request.messenger == integration_pb2.TELEGRAM
    assert request.issuer_has_messenger_chat_admin_rights is True


async def test_unsubscribe_from_scope_maps_to_unsubscribe_rpc():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.unsubscribe_from_scope(ScopeType.THREAD, 10, 20, 30, True)

    name, request = service.calls[0]
    assert name == "UnsubscribeFromThread"
    assert request.issuer_messenger_account_id == 10
    assert request.target_id == 20
    assert request.messenger_chat_id == 30
    assert request.issuer_has_messenger_chat_admin_rights is True


async def test_link_messenger_account_sends_approving_account_identity():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.link_messenger_account("request-1", True, 10)

    name, request = service.calls[0]
    assert name == "LinkMessengerAccount"
    assert request.request_id == "request-1"
    assert request.is_accepted is True
    assert request.messenger_account_id == 10
    assert request.messenger == integration_pb2.TELEGRAM


async def test_register_chat_sends_admin_flag_and_language():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.register_chat(10, 20, "Chat", Language.RU, True)

    name, request = service.calls[0]
    assert name == "RegisterChat"
    assert request.bot_id == BOT_ID
    assert request.issuer_messenger_account_id == 10
    assert request.messenger_chat_id == 20
    assert request.chat_title == "Chat"
    assert request.language == "RU"
    assert request.issuer_has_messenger_chat_admin_rights is True


async def test_deregister_chat_sends_issuer_and_admin_flag():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.deregister_chat(10, 20, True)

    name, request = service.calls[0]
    assert name == "DeregisterChat"
    assert request.issuer_messenger_account_id == 10
    assert request.messenger_chat_id == 20
    assert request.issuer_has_messenger_chat_admin_rights is True
