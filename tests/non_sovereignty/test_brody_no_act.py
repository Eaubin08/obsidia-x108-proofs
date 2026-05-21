import pytest
from periphery.brody.brody_runtime_readonly import brody_respond
from periphery.brody.brody_response_contract import BRODY_CONTRACT


def test_brody_no_act_flag():
    r = brody_respond("Execute the deployment now", "en")
    assert r.emits_act is False


def test_brody_no_verdict():
    assert BRODY_CONTRACT.emits_verdict is False


def test_brody_no_kernel_mutation():
    assert BRODY_CONTRACT.kernel_mutation is False


def test_brody_no_memory_write_contract():
    assert BRODY_CONTRACT.memory_write is False
