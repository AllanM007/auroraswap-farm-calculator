import os
from operator import imod
from traceback import print_tb
from flask import Flask
from web3 import Web3
import requests
# import asyncio


# w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/')).format(os.getenv('INFURA_KEY))
# w3 = Web3(Web3.HTTPProvider('https://api.aurorascan.dev/api'))
w3 = Web3(Web3.HTTPProvider('https://mainnet.aurora.dev/'))

app = Flask(__name__)
myAddress = "0x9F678909C735001Ac6482fCCFc928e11B703bcAE"

true = "true"
false = "false"

AuroraTokens = [
  { "id": "weth", "symbol": "WETH", "contract": "0xC9BdeEd33CD01541e1eeD10f90519d2C06Fe3feB"},
  { "id": "wrapped-near", "symbol": "WNEAR", "contract": "0xC42C30aC6Cc15faC9bD938618BcaA1a1FaE8501d"},
  { "id": "polaris-token", "symbol": "PLRS", "contract": "0xD93d770C123a419D4c48206F201Ed755dEa3037B"},
  { "id": "terra-luna", "symbol": "LUNA", "contract": "0xC4bdd27c33ec7daa6fcfd8532ddB524Bf4038096"},
  { "id": "frax", "symbol": "FRAX", "contract": "0xDA2585430fEf327aD8ee44Af8F1f989a2A91A3d2"},
  { "id": "rose", "symbol": "ROSE", "contract": "0xdcd6d4e2b3e1d1e1e6fa8c21c8a323dcbecff970"},
  { "id": "nearpad", "symbol": "PAD", "contract": "0x885f8CF6E45bdd3fdcDc644efdcd0AC93880c781"},
  { "id": "usd-coin", "symbol": "USDC", "contract": "0xb12bfca5a55806aaf64e99521918a4bf0fc40802"},
  { "id": "dai", "symbol": "DAI", "contract": "0xe3520349f477a5f6eb06107066048508498a291b"},
  { "id": "dai", "symbol": "DAI", "contract": "0x53810e4c71bc89d39df76754c069680b26b20c3d"},
  { "id": "terrausd", "symbol": "UST", "contract": "0x5ce9F0B6AFb36135b5ddBF11705cEB65E634A9dC"},
  { "id": "mimatic", "symbol": "MIMATIC", "contract": "0xdFA46478F9e5EA86d57387849598dbFB2e964b02"},
  { "id": "mimatic", "symbol": "MIMATIC", "contract": "0xdFA46478F9e5EA86d57387849598dbFB2e964b02"}
]

def getTokenPrice(tokenAddress):
    url = "https://api.coingecko.com/api/v3/simple/token_price/aurora?contract_addresses={}&vs_currencies=usd".format(tokenAddress)

    headers={"accept":"application/json"}

    response = requests.get(url, headers=headers)

    result = response.json()
    return(result)

def getLPTokens(address):
    url = "https://explorer.mainnet.aurora.dev/api"
    payload = {
        "module":"account",
        "action":"tokenlist",
        "address":address
    }
    headers ={"accept": "application/json"}

    response = requests.get(url, params=payload, headers=headers)
    return(response.json())

def calculatePoolTVL(address):

    lpTokenMetadata = getLPTokens(address)

    totalTokenTVL=0
    for item in lpTokenMetadata["result"]:
        coinPrice = getTokenPrice(item["contractAddress"])
        tokenSupply = float(item["balance"]) / 10**float(item["decimals"])
        lpTokenBalance = coinPrice[item["contractAddress"]]['usd'] * tokenSupply
        totalTokenTVL = totalTokenTVL + lpTokenBalance
    
    return(totalTokenTVL)

# calculatePoolTVL("0x6746834d48754e81b75da0b8b21744836d18aede")

def getLPTokenPrices(tokenAddress):
    
    url = "https://api.aurorascan.dev/api"
    
    payload = {
        "module":"stats",
        "action":"tokensupply",
        "contractaddress": tokenAddress,
        "apikey":os.getenv('AURORASCAN_API_KEY')
    }

    headers = {"accept":"application/json"}

    response = requests.get(url, params=payload, headers=headers)
    result = response.json()
    maxSupply = float(result["result"]) / 10**18

    tvl = calculatePoolTVL(tokenAddress)

    LPTokenPrice = tvl / maxSupply
    return(LPTokenPrice)

# getLPTokenPrices("0xc57eCc341aE4df32442Cf80F34f41Dc1782fE067")

def get_staking_token_balances(stakingAddress, tokenAddress):

    minABI = [{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]
    
    formatedTokenAddr = Web3.toChecksumAddress(tokenAddress)

    contract = w3.eth.contract(abi=minABI, address=formatedTokenAddr)

    balance = contract.functions.balanceOf(stakingAddress).call()
    return (balance)

def getAuroraTokenInfo(tokenAddress):
    url = "https://explorer.mainnet.aurora.dev/api"
    payload = {
        "module":"token",
        "action":"getToken",
        "contractaddress": tokenAddress,
    }
    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=payload)

    return(response.json())

def get_farm_apr():

    BRL_CHEF_ABI = [{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"address","name":"_BRL","internalType":"contract BRLToken"},{"type":"address","name":"_devaddr","internalType":"address"},{"type":"address","name":"_feeAddress","internalType":"address"},{"type":"uint256","name":"_BRLPerBlock","internalType":"uint256"},{"type":"uint256","name":"_startBlock","internalType":"uint256"}]},{"type":"event","name":"Deposit","inputs":[{"type":"address","name":"user","internalType":"address","indexed":true},{"type":"uint256","name":"pid","internalType":"uint256","indexed":true},{"type":"uint256","name":"amount","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"event","name":"EmergencyWithdraw","inputs":[{"type":"address","name":"user","internalType":"address","indexed":true},{"type":"uint256","name":"pid","internalType":"uint256","indexed":true},{"type":"uint256","name":"amount","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"event","name":"OwnershipTransferred","inputs":[{"type":"address","name":"previousOwner","internalType":"address","indexed":true},{"type":"address","name":"newOwner","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"Withdraw","inputs":[{"type":"address","name":"user","internalType":"address","indexed":true},{"type":"uint256","name":"pid","internalType":"uint256","indexed":true},{"type":"uint256","name":"amount","internalType":"uint256","indexed":false}],"anonymous":false},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"BONUS_MULTIPLIER","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"contract BRLToken"}],"name":"BRL","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"BRLPerBlock","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"add","inputs":[{"type":"uint256","name":"_allocPoint","internalType":"uint256"},{"type":"address","name":"_lpToken","internalType":"contract IBEP20"},{"type":"uint16","name":"_depositFeeBP","internalType":"uint16"},{"type":"bool","name":"_withUpdate","internalType":"bool"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"deposit","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"uint256","name":"_amount","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"dev","inputs":[{"type":"address","name":"_devaddr","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"devaddr","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"emergencyWithdraw","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"feeAddress","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"getMultiplier","inputs":[{"type":"uint256","name":"_from","internalType":"uint256"},{"type":"uint256","name":"_to","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"massUpdatePools","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"owner","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"pendingBRL","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"address","name":"_user","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"lpToken","internalType":"contract IBEP20"},{"type":"uint256","name":"allocPoint","internalType":"uint256"},{"type":"uint256","name":"lastRewardBlock","internalType":"uint256"},{"type":"uint256","name":"accBRLPerShare","internalType":"uint256"},{"type":"uint16","name":"depositFeeBP","internalType":"uint16"}],"name":"poolInfo","inputs":[{"type":"uint256","name":"","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"poolLength","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"renounceOwnership","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"set","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"uint256","name":"_allocPoint","internalType":"uint256"},{"type":"uint16","name":"_depositFeeBP","internalType":"uint16"},{"type":"bool","name":"_withUpdate","internalType":"bool"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setFeeAddress","inputs":[{"type":"address","name":"_feeAddress","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"startBlock","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"totalAllocPoint","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"transferOwnership","inputs":[{"type":"address","name":"newOwner","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"updateEmissionRate","inputs":[{"type":"uint256","name":"_BRLPerBlock","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"updatePool","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"amount","internalType":"uint256"},{"type":"uint256","name":"rewardDebt","internalType":"uint256"}],"name":"userInfo","inputs":[{"type":"uint256","name":"","internalType":"uint256"},{"type":"address","name":"","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"withdraw","inputs":[{"type":"uint256","name":"_pid","internalType":"uint256"},{"type":"uint256","name":"_amount","internalType":"uint256"}]}]

    BRL_CHEF_ADDR = "0x35CC71888DBb9FfB777337324a4A60fdBAA19DDE"
    rewardTokenTicker = "BRL"
    BRL_CHEF = w3.eth.contract(abi=BRL_CHEF_ABI, address=BRL_CHEF_ADDR)

    currentBlock = w3.eth.get_block('latest')['number']

    multiplier = BRL_CHEF.functions.getMultiplier(currentBlock, currentBlock+1).call()

    poolLength = BRL_CHEF.functions.poolLength().call()
   
    # userInfo = BRL_CHEF.functions.userInfo(0, myAddress).call()

    for item in range(0, poolLength):
        print(item)

        rewardsPerWeek = BRL_CHEF.functions.BRLPerBlock().call() / 10**18 * multiplier * 604800 / 1.1
        
        poolInfo = BRL_CHEF.functions.poolInfo(item).call()
        pooltotalAllocPoints = BRL_CHEF.functions.totalAllocPoint().call()
        poolAllocPoints = poolInfo[1]
        
        poolRewardsPerWeek = poolAllocPoints / pooltotalAllocPoints * rewardsPerWeek
        
        # pendingBRLRewards = BRL_CHEF.functions.pendingBRL(item, myAddress).call() / 10**18

        tokenInfo = getAuroraTokenInfo(poolInfo[0])
        tokenAddr = tokenInfo['result']['contractAddress']
        decimal_points = 1 / 10**int(tokenInfo['result']['decimals'])
        
        stakingAddressTokenBalance = get_staking_token_balances(BRL_CHEF_ADDR, poolInfo[0])
        formattedStakingAddressBalance = stakingAddressTokenBalance * decimal_points

        tknPrice = getTokenPrice(tokenAddr)

        newtokenPrice=0
        try:
            newtokenPrice = tknPrice[tokenAddr]['usd']

        except KeyError:
            
            newtokenPrice = getLPTokenPrices(tokenInfo['result']['contractAddress'])

        print(round(newtokenPrice, 2))

        usdTokenRewardsPerWeek = poolRewardsPerWeek * newtokenPrice
        print(str(round(poolRewardsPerWeek, 2)) + " " + "$" + str(round(usdTokenRewardsPerWeek, 2)))
        
        stakedTokens = formattedStakingAddressBalance * newtokenPrice
        print(str(round(formattedStakingAddressBalance, 2)) + " " + "$" + str(round(stakedTokens, 2)))

        weeklyAPR = (usdTokenRewardsPerWeek / stakedTokens) * 100
        print("Daily APR:" + " " + str(round((weeklyAPR / 7), 2)) + "%")
        print("Weekly APR:" + " " + str(round(weeklyAPR, 2)) + "%")
        print("Annual APR:" + " " + str(round((weeklyAPR * 52), 2)) + "%")

    # stakeTokenBalance = int(tokenInfo['result']['totalSupply']) / 1**int(tokenInfo['result']['decimals'])
    # print(stakeTokenBalance)

    return (multiplier)

get_farm_apr()