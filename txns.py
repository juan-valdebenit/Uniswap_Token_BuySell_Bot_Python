from web3 import Web3, IPCProvider
from web3.middleware import geth_poa_middleware
import json
import time
import keys
import sys

# TODO: Add project secret to infura node 
# TODO: Change prints to logging
# TODO: Add testing for edge cases
class Txn_bot():

    def __init__(self, token_address, quantity, net, slippage, gas_price):
        self.net = net
        self.w3 = self.connect()
        print("Access to Infura node: {}".format((self.w3.is_connected())))
        self.address, self.private_key = self.set_address()
        print("Address: {}".format(self.address))
        print("Current balance of WETH/WBNB: {}".format(self.w3.from_wei(self.w3.eth.get_balance(self.address), 'ether')))
        self.token_address = Web3.to_checksum_address(token_address)
        self.token_contract = self.set_token_contract()
        print("Current balance of {}: {}".format(self.token_contract.functions.symbol().call() ,self.token_contract.functions.balanceOf(self.address).call() / (10 ** self.token_contract.functions.decimals().call())))
        self.router_address, self.router = self.set_router()
        self.quantity = int(quantity)
        self.slippage = 1 - (slippage/100)
        self.gas_price = gas_price

    def connect(self):
        if self.net=="1":
            w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/{}".format(keys.infura_project_id)))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        elif self.net=="4":
            w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/{}".format(keys.infura_project_id)))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        elif self.net=="2":
            w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
        elif self.net=="3":
            w3 = Web3(Web3.HTTPProvider("https://arb1.arbitrum.io/rpc"))
        # TODO: Add bsc-tesnet. Cake testing problems
        else:
            print("Not a valid network...\nSupported networks: eth-mainnet, eth-rinkeby, bsc-mainnet")
            sys.exit()
        return w3

    def set_address(self):
        return(keys.metamask_address, keys.metamask_private_key)

    def set_router(self):   #TODO: Refactor functions into shorter ones?
        if "1" in self.net:
            router_address = Web3.to_checksum_address("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
            with open("./abis/IUniswapV2Router02.json") as f:
                contract_abi = json.load(f)['abi']
            router = self.w3.eth.contract(address=router_address, abi=contract_abi)
        if "2" in self.net:
            router_address = Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E") # mainnet router
            with open("./abis/pancakeRouter.json") as f:
                contract_abi = json.load(f)['abi']
            router = self.w3.eth.contract(address=router_address, abi=contract_abi)
        if "3" in self.net:
            router_address = Web3.to_checksum_address("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D") # mainnet router
            with open("./abis/pancakeRouter.json") as f:
                contract_abi = json.load(f)['abi']
            router = self.w3.eth.contract(address=router_address, abi=contract_abi)
        if "4" in self.net:
            router_address = Web3.to_checksum_address("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D") # mainnet router
            with open("./abis/pancakeRouter.json") as f:
                contract_abi = json.load(f)['abi']
            router = self.w3.eth.contract(address=router_address, abi=contract_abi)
        return (router_address, router)

    def set_token_contract(self): #TODO: Refactor functions into shorter ones?
        if "1" in self.net:
            token_address = Web3.to_checksum_address(self.token_address)
            with open("./abis/erc20_abi.json") as f:
                contract_abi = json.load(f)
            token_contract = self.w3.eth.contract(address=token_address, abi=contract_abi)
        else:
            token_address = Web3.to_checksum_address(self.token_address)
            with open("./abis/bep20_abi_token.json") as f:
                contract_abi = json.load(f)
            token_contract = self.w3.eth.contract(address=token_address, abi=contract_abi)
        return token_contract

    def get_amounts_out_buy(self):
        return self.router.functions.getAmountsOut(
            int(int(self.quantity) * self.slippage),
            [self.router.functions.WETH().call(), self.token_address]
            ).call()

    def get_amounts_out_sell(self):
        return self.router.functions.getAmountsOut(
            self.token_contract.functions.balanceOf(self.address).call(),
            [self.token_address, self.router.functions.WETH().call()]
            ).call()

    def approve(self):
        gas_price = self.w3.eth.gas_price
        txn = self.token_contract.functions.approve(
            self.router_address,
            2**256 - 1
        ).build_transaction(
            {'from': self.address, 
            'gas': 250000,
            'gasPrice': gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address), 
            'value': 0}
            )
        
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print("Approve Success",txn.hex())
        txn_receipt = self.w3.eth.wait_for_transaction_receipt(txn)

    def buy_token(self):
        gas_price = self.w3.eth.gas_price
        txn = self.router.functions.swapExactETHForTokens(
            0,
            [self.router.functions.WETH().call(), self.token_address], 
            bytes.fromhex(self.address[2:]), 
            int(time.time()) + 10 * 60 # 10 min limit
        ).build_transaction(
            {'from': self.address, 
            'gas': 250000,
            'gasPrice': gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address), 
            'value': int(self.quantity)}
            )
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print("buy success!", txn.hex())
        txn_receipt = self.w3.eth.wait_for_transaction_receipt(txn)

    def sell_token(self):
        gas_price = self.w3.eth.gas_price
        txn = self.router.functions.swapExactTokensForETH(
            self.token_contract.functions.balanceOf(self.address).call(),
            int(self.get_amounts_out_sell()[-1] * self.slippage),
            [self.token_address, self.router.functions.WETH().call()], 
            bytes.fromhex(self.address[2:]), 
            int(time.time()) + 10 * 60 # 10 min limit
        ).build_transaction(
            {'from': self.address, 
            'gas': 250000,
            'gasPrice': gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address), 
            'value': 0}
            )

        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print("Sell Success", txn.hex())
        txn_receipt = self.w3.eth.wait_for_transaction_receipt(txn)

    def check_price_busd_usdc(self):
        if (self.net == "1"):
            return self.router.functions.getAmountsOut(
                int(1*10**18),
                [self.token_address, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"]
                ).call()[1]
        elif (self.net == "2"):
            return self.router.functions.getAmountsOut(
                int(1*10**18),
                [self.token_address, "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"]
                ).call()[1]
