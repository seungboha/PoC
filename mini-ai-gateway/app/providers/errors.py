class ProviderCreditExhaustedError(Exception):
    """Raised when a provider cannot run because its credit is exhausted."""


class ProviderConfigurationError(Exception):
    """Raised when a selected provider is not configured correctly."""
