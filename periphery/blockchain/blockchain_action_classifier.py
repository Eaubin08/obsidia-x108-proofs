"""
Blockchain Action Classifier — classifies blockchain-related actions by risk level.
All results are advisory. No real chain actions are taken.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class BlockchainActionClass(str, Enum):
    CHAIN_READ_ONLY = "CHAIN_READ_ONLY"
    WALLET_CONNECT_REQUEST = "WALLET_CONNECT_REQUEST"
    SIGN_MESSAGE_REQUEST = "SIGN_MESSAGE_REQUEST"
    SIGN_TRANSACTION_REQUEST = "SIGN_TRANSACTION_REQUEST"
    TOKEN_TRANSFER = "TOKEN_TRANSFER"
    TOKEN_APPROVAL = "TOKEN_APPROVAL"
    TOKEN_MINT = "TOKEN_MINT"
    TOKEN_BURN = "TOKEN_BURN"
    SMART_CONTRACT_CALL = "SMART_CONTRACT_CALL"
    SMART_CONTRACT_DEPLOY = "SMART_CONTRACT_DEPLOY"
    BRIDGE_TRANSFER = "BRIDGE_TRANSFER"
    DEFI_SWAP = "DEFI_SWAP"
    DEFI_STAKE = "DEFI_STAKE"
    DEFI_BORROW = "DEFI_BORROW"
    ORACLE_DEPENDENT_ACTION = "ORACLE_DEPENDENT_ACTION"
    DAO_VOTE = "DAO_VOTE"
    UNKNOWN_CHAIN_ACTION = "UNKNOWN_CHAIN_ACTION"


_BLOCK_CLASSES = {
    BlockchainActionClass.SIGN_MESSAGE_REQUEST,
    BlockchainActionClass.SIGN_TRANSACTION_REQUEST,
    BlockchainActionClass.TOKEN_MINT,
    BlockchainActionClass.SMART_CONTRACT_DEPLOY,
    BlockchainActionClass.BRIDGE_TRANSFER,
}

_HOLD_CLASSES = {
    BlockchainActionClass.WALLET_CONNECT_REQUEST,
    BlockchainActionClass.TOKEN_APPROVAL,
    BlockchainActionClass.TOKEN_TRANSFER,
    BlockchainActionClass.TOKEN_BURN,
    BlockchainActionClass.SMART_CONTRACT_CALL,
    BlockchainActionClass.DEFI_SWAP,
    BlockchainActionClass.DEFI_STAKE,
    BlockchainActionClass.DEFI_BORROW,
    BlockchainActionClass.ORACLE_DEPENDENT_ACTION,
    BlockchainActionClass.DAO_VOTE,
    BlockchainActionClass.UNKNOWN_CHAIN_ACTION,
}


@dataclass
class BlockchainActionDecision:
    action_id: str
    action_class: str
    gate: str
    reason: str
    dry_run_only: bool = True
    real_chain_action_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_class": self.action_class,
            "gate": self.gate,
            "reason": self.reason,
            "dry_run_only": self.dry_run_only,
            "real_chain_action_allowed": self.real_chain_action_allowed,
        }


def classify_blockchain_action(action_id: str, action_class: BlockchainActionClass) -> BlockchainActionDecision:
    if action_class in _BLOCK_CLASSES:
        return BlockchainActionDecision(
            action_id=action_id,
            action_class=action_class.value,
            gate="BLOCK",
            reason=f"BLOCKCHAIN_ACTION_BLOCKED_V4:{action_class.value}",
        )
    if action_class in _HOLD_CLASSES:
        return BlockchainActionDecision(
            action_id=action_id,
            action_class=action_class.value,
            gate="HOLD",
            reason=f"BLOCKCHAIN_ACTION_HOLD_REQUIRES_REVIEW:{action_class.value}",
        )
    return BlockchainActionDecision(
        action_id=action_id,
        action_class=action_class.value,
        gate="ALLOW",
        reason="CHAIN_READ_ONLY_PERMITTED",
    )
