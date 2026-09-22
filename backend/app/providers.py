import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class ProviderQuote:
    instrument_id: str; provider: str; series_id: str; quote_type: str; value: Decimal
    currency: str; unit: str; as_of: datetime; received_at: datetime; status: str = "fresh"
    bid: Decimal | None = None; ask: Decimal | None = None; valuation_date: datetime | None = None


class MarketDataProvider(ABC):
    @abstractmethod
    def quotes(self, step: int = 0) -> list[ProviderQuote]: ...


class DemoProvider(MarketDataProvider):
    """Tekrarlanabilir sentetik seri; gerçek moda sessiz geçiş yoktur."""
    base = {"usdtry": Decimal("41.20"), "eurtry": Decimal("48.60"), "xu030": Decimal("11850"),
            "xu100": Decimal("10950"), "thyao": Decimal("318.25"), "akb": Decimal("6.543210")}
    def quotes(self, step: int = 0) -> list[ProviderQuote]:
        now = datetime.now(UTC).replace(microsecond=0); result = []
        meta = {"usdtry": ("fx_mid", "TRY", "para"), "eurtry": ("fx_mid", "TRY", "para"),
                "xu030": ("index_level", "POINT", "puan"), "xu100": ("index_level", "POINT", "puan"),
                "thyao": ("last_trade", "TRY", "para"), "akb": ("fund_unit_value", "TRY", "pay")}
        for i, (key, base) in enumerate(self.base.items()):
            value = base * Decimal(str(1 + 0.002 * math.sin(step + i)))
            typ, cur, unit = meta[key]
            result.append(ProviderQuote(key, "demo-synthetic", f"demo:{key}:v1", typ, value.quantize(Decimal("0.000001")), cur, unit, now, now, valuation_date=(now - timedelta(days=1) if key == "akb" else None), bid=value-Decimal("0.01") if "try" in key else None, ask=value+Decimal("0.01") if "try" in key else None))
        return result


def get_provider(name: str) -> MarketDataProvider:
    if name == "demo": return DemoProvider()
    raise RuntimeError(f"'{name}' gerçek sağlayıcısı yapılandırılmadı; DEMO'ya geçilmedi")

