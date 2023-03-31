from web3.middleware import geth_poa_middleware
from web3 import Web3
import time
from discord_webhook import DiscordWebhook
import json

class pcsInteraction:
	def __init__(self) -> None:
		self.w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
		self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		self.nbLooses = 0
		# Initialize the contract
		with open("abi_PCS.json","r") as fp:
			self.abiPCS = json.load(fp)
		with open("abi_Oracle.json","r") as f:
			self.abiOracle = json.load(f)
		with open("config.json","r") as f:
			self.config = json.load(f)
		self.contract = self.w3.eth.contract('0x18B2A687610328590Bc8F2e5fEdDe3b582A49cdA', abi=self.abiPCS)
		self.contractOracle = self.w3.eth.contract('0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE', abi=self.abiOracle)
		self.private_key = self.config["privateKey"]
		self.valueBet = self.config["betAmt"]

	def betBull(self):
		try:
			tx = self.contract.functions.betBull(self.currentEpoch()).buildTransaction({
				'from': self.config["publicKey"],
				"nonce": self.w3.eth.getTransactionCount(self.config["publicKey"]),
				"value": self.valueBet,
				'gas': '0',
				'gasPrice': self.w3.toWei(self.config["gweiGas"],"gwei")
			})

			gas = self.w3.eth.estimate_gas(tx)
			tx.update({ 'gas' : gas })
			# Sign transaction with wallet
			signed_tx = self.w3.eth.account.signTransaction(tx, self.private_key)

			# Send transaction to network
			tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

			# Wait for transaction to be mined
			receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
			balance = self.getBalance()
			webhook = DiscordWebhook(url=self.config["webHookUrl"], content=f"Betting BULL :ox: ```current balance : {balance} BNB```")
			webhook.execute()
		except Exception as e:
			print(e)
			exit()

	def getBalance(self):
		return self.w3.fromWei(self.w3.eth.get_balance(self.config["publicKey"]),"Ether")

	def getOraclePrice(self):
		return self.contractOracle.functions.latestRoundData().call()[1]/100000000

	def betBear(self):
		try:
			tx = self.contract.functions.betBear(self.currentEpoch()).buildTransaction({
				'from': self.config["publicKey"],
				"nonce": self.w3.eth.getTransactionCount(self.config["publicKey"]),
				"value": self.valueBet,
				'gas': '0',
				'gasPrice': self.w3.toWei(self.config["gweiGas"],"gwei")
			})
			gas = self.w3.eth.estimate_gas(tx)
			tx.update({ 'gas' : gas })

			# Sign transaction with wallet
			signed_tx = self.w3.eth.account.signTransaction(tx, self.private_key)

			# Send transaction to network
			tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

			# Wait for transaction to be mined
			receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
			balance = self.getBalance()
			webhook = DiscordWebhook(url=self.config["webHookUrl"], content=f"Betting BEAR :bear: ```current balance : {balance} BNB```")
			webhook.execute()
		except Exception as e:
			print(e)
			exit()

	
	def currentEpoch(self):
		return self.contract.functions.currentEpoch().call()
	
	def userLastRounds(self,length=1):
		userAddr = self.config["publicKey"]
		roundSlength = self.contract.functions.getUserRoundsLength(userAddr).call()
		result = self.contract.functions.getUserRounds(userAddr,roundSlength-length,length).call()
		arrOut = []
		arrIds = result[0]
		arrRounds = result[1]
		roundIndex = 0
		for round in arrRounds:
			if round[0] == 0:
				direction = "UP"
			else :
				direction = "DOWN"
			obj = {"id":arrIds[roundIndex],"direction":direction,"win":round[2]}
			arrOut.append(obj)
			roundIndex +=1
		return arrOut
	
	def isClaimable(self,roundId):
		return self.contract.functions.claimable(roundId,self.config["publicKey"]).call()

	def claim(self):
		try:
			lastRound = self.currentEpoch()-2
			if self.isClaimable(int(lastRound)) == True:
				print(f"claiming winings from round {lastRound}")
				tx = self.contract.functions.claim([lastRound]).buildTransaction({
					'from': self.config["publicKey"],
					"nonce": self.w3.eth.getTransactionCount(self.config["publicKey"]),
					"value": 0,
					'gas': '0',
					'gasPrice': self.w3.toWei('5', 'gwei')
				})
				gas = self.w3.eth.estimate_gas(tx)
				tx.update({ 'gas' : gas })

				# Sign transaction with wallet
				signed_tx = self.w3.eth.account.signTransaction(tx, self.private_key)

				# Send transaction to network
				tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

				# Wait for transaction to be mined
				receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
				time.sleep(5)
				balance = self.getBalance()
				webhook = DiscordWebhook(url=self.config["webHookUrl"], content=f":money_mouth: ROUND WON :money_mouth: ```current balance : {balance} BNB```")
				webhook.execute()
				self.valueBet = self.config["betAmt"]
				self.nbLooses=0
			if self.nbLooses > 0:
				self.valueBet = self.config["betAmt"]*(self.nbLooses)
		except Exception as e:
			print(e)
			if self.nbLooses > 0:
				self.valueBet = self.config["betAmt"]*(self.nbLooses)
			return False
		
	def getTimeLeft(self):
		currEpoch = self.currentEpoch()
		return self.contract.functions.rounds(currEpoch).call()[2]-int(round(time.time(),0))