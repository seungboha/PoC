from collections.abc import Callable

from app.config import Settings
from app.providers.base import AIProvider
from app.providers.factory import create_provider

POLICY_PROVIDER_NAMES = {
    "speed": "mock",
    "quality": "openai",
    "cost": "mock",
}
SUPPORTED_ROUTING_POLICIES = tuple(POLICY_PROVIDER_NAMES)

ProviderFactory = Callable[[Settings, str | None], AIProvider]


class UnsupportedRoutingPolicyError(ValueError):
    def __init__(self, policy: str) -> None:
        self.policy = policy
        super().__init__(f"Unsupported routing policy: {policy}")


class ProviderRouter:
    def __init__(
        self,
        settings: Settings,
        provider_factory: ProviderFactory = create_provider,
    ) -> None:
        self.settings = settings
        self.provider_factory = provider_factory
        self.default_provider = provider_factory(settings, None)
        self.providers: dict[str, AIProvider] = {
            self.default_provider.name: self.default_provider,
        }

    def resolve(self, routing_policy: str | None) -> AIProvider:
        if routing_policy is None:
            return self.default_provider

        normalized_policy = routing_policy.strip().lower()
        provider_name = POLICY_PROVIDER_NAMES.get(normalized_policy)

        if provider_name is None:
            raise UnsupportedRoutingPolicyError(routing_policy)

        if provider_name not in self.providers:
            self.providers[provider_name] = self.provider_factory(
                self.settings,
                provider_name,
            )

        return self.providers[provider_name]
