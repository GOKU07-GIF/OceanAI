from __future__ import annotations

from typing import Any, Protocol, Sequence

from app.orca.marine.incois import incois_provider
from app.orca.marine.models import MARINE_VARIABLES, MarineConditions, MarineDataRequest


class MarineProvider(Protocol):
    """Contract implemented by each authoritative marine data source."""

    name: str

    def fetch(self, request: MarineDataRequest) -> dict[str, Any]:
        """Return a provider result using the canonical ORCA marine shape."""
        ...


class MarineProviderRegistry:
    """Small registry used to keep source-specific code out of agents."""

    def __init__(self) -> None:
        self._providers: dict[str, MarineProvider] = {}

    def register(self, provider: MarineProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> MarineProvider | None:
        return self._providers.get(name)

    def ordered(self, names: Sequence[str]) -> list[MarineProvider]:
        return [provider for name in names if (provider := self.get(name)) is not None]

    def names(self) -> list[str]:
        return list(self._providers)


class CompositeMarineProvider:
    """Try configured providers in order and preserve provenance/failures."""

    def __init__(self, registry: MarineProviderRegistry) -> None:
        self.registry = registry

    def fetch(
        self,
        *,
        request: MarineDataRequest,
        provider_order: Sequence[str],
    ) -> dict[str, Any]:
        requested = [
            variable
            for variable in request.get("variables", [])
            if variable in MARINE_VARIABLES
        ]
        missing = list(requested)
        errors: list[dict[str, str]] = []

        providers = self.registry.ordered(provider_order)
        if not providers:
            return {
                "status": "unavailable",
                "data": None,
                "missing_variables": missing or list(MARINE_VARIABLES),
                "errors": [{
                    "source": "registry",
                    "error": "No marine data provider is registered for this request.",
                }],
            }

        for provider in providers:
            try:
                result = provider.fetch(request)
            except Exception as exc:  # pragma: no cover - defensive provider boundary
                errors.append({"source": provider.name, "error": str(exc)})
                continue

            if result.get("status") != "success":
                errors.append({
                    "source": provider.name,
                    "error": str(result.get("error", "Provider returned an unsuccessful status.")),
                })
                continue

            data = result.get("data")
            if not isinstance(data, dict):
                errors.append({
                    "source": provider.name,
                    "error": "Provider returned success without a canonical data object.",
                })
                continue

            normalized = normalize_marine_conditions(data, fallback_source=provider.name)
            present = [key for key in missing if normalized.get(key) is not None]
            remaining = [key for key in missing if key not in present]

            return {
                "status": "success",
                "data": normalized,
                "missing_variables": remaining,
                "errors": errors,
                "provider": provider.name,
            }

        return {
            "status": "unavailable",
            "data": None,
            "missing_variables": missing or list(MARINE_VARIABLES),
            "errors": errors,
        }


def normalize_marine_conditions(
    payload: dict[str, Any],
    *,
    fallback_source: str,
) -> MarineConditions:
    """Normalize a provider payload without inventing absent marine values."""
    normalized: MarineConditions = {
        "source": str(payload.get("source") or fallback_source),
        "dataset": str(payload.get("dataset") or "unknown"),
        "type": payload.get("type", "mixed"),
        "quality": str(payload.get("quality") or "unknown"),
        "metadata": dict(payload.get("metadata") or {}),
    }

    for key in (
        "location",
        "timestamp",
        "retrieved_at",
        "wave_height_m",
        "swell_height_m",
        "wave_period_s",
        "current_speed_ms",
        "current_direction_deg",
        "sst_c",
        "chlorophyll_mg_m3",
        "pfz_available",
        "advisories",
    ):
        if key in payload and payload[key] is not None:
            normalized[key] = payload[key]

    return normalized


marine_provider_registry = MarineProviderRegistry()
marine_provider_registry.register(incois_provider)
marine_provider = CompositeMarineProvider(marine_provider_registry)
