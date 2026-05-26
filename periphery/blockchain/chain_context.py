"""
Chain Context — readonly chain environment descriptor.
No real RPC calls. Context candidate only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ChainContext:
    chain_id: str
    chain_name: str
    is_mainnet: bool
    is_testnet: bool
    block_height: int | None
    gas_price_gwei: float | None
    read_only: bool = True
    real_rpc_connected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "chain_name": self.chain_name,
            "is_mainnet": self.is_mainnet,
            "is_testnet": self.is_testnet,
            "block_height": self.block_height,
            "gas_price_gwei": self.gas_price_gwei,
            "read_only": self.read_only,
            "real_rpc_connected": self.real_rpc_connected,
        }


_CHAIN_REGISTRY: dict[str, dict] = {
    "1": {"name": "ethereum_mainnet", "mainnet": True, "testnet": False},
    "5": {"name": "goerli", "mainnet": False, "testnet": True},
    "11155111": {"name": "sepolia", "mainnet": False, "testnet": True},
    "137": {"name": "polygon_mainnet", "mainnet": True, "testnet": False},
    "80001": {"name": "polygon_mumbai", "mainnet": False, "testnet": True},
    "56": {"name": "bsc_mainnet", "mainnet": True, "testnet": False},
    "43114": {"name": "avalanche_mainnet", "mainnet": True, "testnet": False},
}


def build_chain_context(chain_id: str) -> ChainContext:
    info = _CHAIN_REGISTRY.get(chain_id, {"name": f"unknown_{chain_id}", "mainnet": False, "testnet": False})
    return ChainContext(
        chain_id=chain_id,
        chain_name=info["name"],
        is_mainnet=info["mainnet"],
        is_testnet=info["testnet"],
        block_height=None,
        gas_price_gwei=None,
        read_only=True,
        real_rpc_connected=False,
    )
