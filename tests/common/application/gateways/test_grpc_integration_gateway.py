from unittest.mock import Mock, patch

from common.application.enums import Language, Messenger
from common.application.gateways.grpc_integration_gateway import GrpcIntegrationGateway
from common.application.protocols.integration_gateway import (
    ChatPreferences,
    ChatPreferenceUpdates,
    ScopeType,
)
from common.config.schemas.grpc_config import GrpcConfig
from common.config.schemas.tls_config import TlsConfig
from common.infrastructure.grpc.generated import integration_pb2

BOT_ID: int = 42


def _grpc_config(target: str) -> GrpcConfig:
    return GrpcConfig(
        target=target,
        timeout=5.0,
        tls=TlsConfig(
            enabled=False,
            ca_certificate=None,
            certificate=None,
            private_key=None,
        ),
    )


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

    async def UpdateChatInfo(self, request, **kwargs):
        self.calls.append(("UpdateChatInfo", request))
        return self._response()

    def _response(self):
        return integration_pb2.GeneralResponse(
            key="register_chat.success", locale=integration_pb2.EN
        )


def _gateway(service: RecordingIntegrationService) -> GrpcIntegrationGateway:
    gateway = GrpcIntegrationGateway(
        _grpc_config("localhost:0"),
        bot_id=BOT_ID,
        messenger=Messenger.TELEGRAM,
        fallback_language=Language.EN,
    )
    gateway._integration_service = service  # pyright: ignore[reportAttributeAccessIssue]
    return gateway


async def test_start_opens_insecure_channel_when_tls_is_disabled():
    gateway = GrpcIntegrationGateway(
        _grpc_config("localhost:9090"),
        bot_id=BOT_ID,
        messenger=Messenger.TELEGRAM,
        fallback_language=Language.EN,
    )
    channel = Mock()

    with (
        patch(
            "common.application.gateways.grpc_integration_gateway.grpc.aio.insecure_channel",
            return_value=channel,
        ) as insecure_channel,
        patch(
            "common.application.gateways.grpc_integration_gateway.integration_pb2_grpc.IntegrationServiceStub"
        ),
    ):
        await gateway.start()

    insecure_channel.assert_called_once_with("localhost:9090")


async def test_start_opens_mutual_tls_channel_when_configured(tmp_path):
    ca_certificate = tmp_path / "ca.crt"
    certificate = tmp_path / "client.crt"
    private_key = tmp_path / "client.key"
    ca_certificate.write_bytes(b"ca")
    certificate.write_bytes(b"certificate")
    private_key.write_bytes(b"private key")
    gateway = GrpcIntegrationGateway(
        GrpcConfig(
            target="localhost:9090",
            timeout=5.0,
            tls=TlsConfig(
                enabled=True,
                ca_certificate=ca_certificate,
                certificate=certificate,
                private_key=private_key,
            ),
        ),
        bot_id=BOT_ID,
        messenger=Messenger.TELEGRAM,
        fallback_language=Language.EN,
    )
    credentials = Mock()
    channel = Mock()

    with (
        patch(
            "common.application.gateways.grpc_integration_gateway.grpc.ssl_channel_credentials",
            return_value=credentials,
        ) as ssl_channel_credentials,
        patch(
            "common.application.gateways.grpc_integration_gateway.grpc.aio.secure_channel",
            return_value=channel,
        ) as secure_channel,
        patch(
            "common.application.gateways.grpc_integration_gateway.integration_pb2_grpc.IntegrationServiceStub"
        ),
    ):
        await gateway.start()

    ssl_channel_credentials.assert_called_once_with(
        root_certificates=b"ca",
        private_key=b"private key",
        certificate_chain=b"certificate",
    )
    secure_channel.assert_called_once_with("localhost:9090", credentials)


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


async def test_register_chat_sends_admin_flag_language_and_time_zone():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.register_chat(
        10, 20, "Chat", ChatPreferences(Language.RU, "Europe/Moscow"), True
    )

    name, request = service.calls[0]
    assert name == "RegisterChat"
    assert request.bot_id == BOT_ID
    assert request.issuer_messenger_account_id == 10
    assert request.messenger_chat_id == 20
    assert request.chat_title == "Chat"
    assert request.language == "RU"
    assert request.time_zone == "Europe/Moscow"
    assert request.issuer_has_messenger_chat_admin_rights is True


async def test_update_chat_info_preserves_optional_field_presence():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.update_chat_info(
        10, 20, True, "Chat", ChatPreferenceUpdates(time_zone="Asia/Kathmandu")
    )

    name, request = service.calls[0]
    assert name == "UpdateChatInfo"
    assert request.HasField("title")
    assert request.title == "Chat"
    assert not request.HasField("language")
    assert request.HasField("time_zone")
    assert request.time_zone == "Asia/Kathmandu"


async def test_update_chat_info_omits_both_unset_optional_preferences():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.update_chat_info(10, 20, True, "Chat", ChatPreferenceUpdates())

    _, request = service.calls[0]
    assert not request.HasField("language")
    assert not request.HasField("time_zone")


async def test_deregister_chat_sends_issuer_and_admin_flag():
    service = RecordingIntegrationService()
    gateway = _gateway(service)

    await gateway.deregister_chat(10, 20, True)

    name, request = service.calls[0]
    assert name == "DeregisterChat"
    assert request.issuer_messenger_account_id == 10
    assert request.messenger_chat_id == 20
    assert request.issuer_has_messenger_chat_admin_rights is True
