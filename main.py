from txns import Txn_bot
import time


token_address = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
quantity = 1300000000000000
net = 'eth-goerli'
slippage = 30
gas_price = 20 * 10**9 #Gwei, bsc-mainnet=5, eth-mainnet=https://www.gasnow.org/, eth-rinkeby=1f
delay = 10

bot = Txn_bot(token_address, quantity, net, slippage, gas_price)
tokens = bot.get_amounts_out_buy()
bot.buy_token()
bot.approve()
time.sleep(delay)
bot.sell_token()


