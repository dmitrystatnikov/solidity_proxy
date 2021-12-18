from scripts.helpers import get_account, is_local_blockchain_env
from brownie import (
    StorageBox,
    StorageBoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    network,
    config,
)

from_account = {"from": get_account()}
network_configuration = config["networks"][network.show_active()]


def deploy_boxes():
    if len(StorageBox) == 0:
        StorageBox.deploy(
            from_account, publish_source=network_configuration.get("verify")
        )
    if len(StorageBoxV2) == 0:
        StorageBoxV2.deploy(
            from_account, publish_source=network_configuration.get("verify")
        )


def deploy_proxy_admin():
    if len(ProxyAdmin) == 0:
        ProxyAdmin.deploy(
            from_account, publish_source=network_configuration.get("verify")
        )


def create_initializer(initializer=None, *args):
    if not initializer:
        return bytes()
    else:
        return initializer.encode_input(*args)


def deploy_proxy(contract, admin, data_initializer):
    if len(TransparentUpgradeableProxy) == 0:
        TransparentUpgradeableProxy.deploy(
            contract.address,
            admin.address,
            data_initializer,
            from_account,
            publish_source=network_configuration.get("verify"),
        )


def deploy_storage_contract(implementation):
    if is_local_blockchain_env():
        return Contract.from_abi(
            "Storage Box", TransparentUpgradeableProxy[-1].address, implementation.abi
        )
    else:
        return Contract.from_explorer(
            TransparentUpgradeableProxy[-1].address, implementation.address
        )


def upgrade_contract(admin, proxy, implementation):
    tx = admin.upgrade(proxy, implementation.address, from_account)
    tx.wait(1)


def main():
    deploy_boxes()
    deploy_proxy_admin()
    initializer = create_initializer(StorageBox[-1].store, 0x10)
    deploy_proxy(StorageBox[-1], ProxyAdmin[-1], initializer)
    contract = deploy_storage_contract(StorageBox[-1])
    print(f"Stored value: {contract.retrieve()}")

    upgrade_contract(ProxyAdmin[-1], TransparentUpgradeableProxy[-1], StorageBoxV2[-1])

    contract = deploy_storage_contract(StorageBoxV2[-1])
    contract.increase(from_account)
    print(f"Stored value: {contract.retrieve()}")
