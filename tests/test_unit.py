from scripts.deployment import (
    deploy_boxes,
    deploy_proxy_admin,
    deploy_proxy,
    deploy_storage_contract,
    create_initializer,
    upgrade_contract,
)
from scripts.helpers import get_account, is_local_blockchain_env
from brownie import StorageBox, StorageBoxV2, ProxyAdmin, TransparentUpgradeableProxy
import pytest

stored_value = 7


def test_proxy_creation():
    if not is_local_blockchain_env():
        pass
    deploy_boxes()
    deploy_proxy_admin()
    initializer = create_initializer(StorageBox[-1].store, stored_value)
    deploy_proxy(StorageBox[-1], ProxyAdmin[-1], initializer)
    contract = deploy_storage_contract(StorageBox[-1])

    assert contract.retrieve() == stored_value
    with pytest.raises(AttributeError):
        contract.increase({"from": get_account()})

    upgrade_contract(ProxyAdmin[-1], TransparentUpgradeableProxy[-1], StorageBoxV2[-1])
    contract = deploy_storage_contract(StorageBoxV2[-1])

    value = contract.retrieve()
    assert stored_value == value

    contract.increase({"from": get_account()})
    assert contract.retrieve() == value + 1
