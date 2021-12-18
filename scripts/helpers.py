from brownie import (
    accounts,
    network,
    config,
)


def is_local_blockchain_env():
    return network.show_active() in ["development", "ganache-local"]


def is_local_forked_env():
    return network.show_active() in ["mainnet-fork-alchemy", "mainnet-fork-aave"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if not is_local_blockchain_env() and not is_local_forked_env():
        return accounts.add(config["wallets"]["from_key"])
    return accounts[0]
