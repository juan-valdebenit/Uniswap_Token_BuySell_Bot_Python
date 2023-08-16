from txns import Txn_bot
import time


#token_address = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
#quantity = 1300000000000000
#net = 'eth-goerli'
slippage = 30
gas_price = 40 * 10 ** 9  #Gwei, bsc-mainnet=5, eth-mainnet=https://www.gasnow.org/, eth-rinkeby=1f
delay = 10

net = input("Choose Chain Ethereum : 1, BSC : 2, Arbitrum-Mainnet : 3, Goerli-Testnet : 4,  Choose one : ")
token_address = input("Enter Address of Token:")
quantity = input ("Input Amount of ETH/BNB To Buy Token :" )
quantity = float(quantity) * 1000000000000000000
delay = input("Please input time delay between buy and sell transaction (second)")


bot = Txn_bot(token_address, quantity, net, slippage, gas_price)
tokens = bot.get_amounts_out_buy()
bot.buy_token()
bot.approve()
time.sleep(int(delay))
bot.sell_token()


