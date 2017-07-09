import crackcoin
import crackcoin.wallets

from hashlib import sha512
import json
from time import time
from os import urandom


TRANSACTION_HASH_LENGTH = 32
VALIDATION_ADDITION_LENGTH = 20

def getJSONForTransaction(transactionHash):
	''' Create JSON data for transaction '''

	transaction = crackcoin.db.doQuery("SELECT hash,timestamp from transactions WHERE hash = ?", (transactionHash,), result='one')
	timestamp = transaction[1]

	JSONDict = {}
	JSONDict['inputs'] = []
	JSONDict['outputs'] = []

	JSONDict['transactionHash'] = transactionHash
	JSONDict['timestamp'] = timestamp

	inputs = crackcoin.db.doQuery("SELECT previousOutput, publicKey, timestamp, signature from transactions_inputs WHERE transactionHash = ?", (transactionHash,), result='all')
	for inputTransaction in inputs:
		previousOutput, publicKey, timestamp, signature = inputTransaction

		inputDict = {'previousOutput':previousOutput, 'publicKey':publicKey, 'timestamp':timestamp, 'signature':signature}
		JSONDict['inputs'].append(inputDict)

	outputs = crackcoin.db.doQuery("SELECT amount, address, outputHash from transactions_outputs WHERE transactionHash = ?", (transactionHash,), result='all')
	for outputTransaction in outputs:
		amount, address, outputHash = outputTransaction

		outputDict = {'amount':str(amount), 'address':address, 'outputHash':outputHash}
		JSONDict['outputs'].append(outputDict)

	transactionJSON = json.dumps(JSONDict)
	transactionJSON.replace(' ','')
	return transactionJSON



def addTransactionJSON(data):
	''' Add a new transaction from JSON data '''
	
	transaction = json.loads(data)

	transactionHash = transaction['transactionHash']
	
	# validation todo: check if transaction already exists

	
	transactionTimestamp = transaction['timestamp']

	# validation todo: timestamp must be sane
	
	totalInputAmount = 0

	for oldInput in transaction['inputs']:
		outputHash = oldInput['previousOutput']

		# validation todo: input must have at least 20 confirmations
		
		# input must exist
		amount, address = crackcoin.db.doQuery("SELECT amount, address from transactions_outputs WHERE outputHash = ?", (outputHash,), result='one')
		totalInputAmount += amount

		# validation: old input must not already exist in outputs

		publicKey = oldInput['publicKey']

		# validation todo: convert public key to address and check if address match for old output!


		# timestamp must be the same as transaction
		timestamp = oldInput['timestamp']
		if timestamp != transactionTimestamp:
			print "error3"
			return False

		signature = oldInput['signature']
		signature = signature.replace(' ','').replace('(','').replace(')','').split(',')
		signature = (long(signature[0]), long(signature[1]))
		
		# validate signature
		message = outputHash + publicKey + timestamp

		publicKey = crackcoin.wallets.decompressPublicKey(publicKey)

		signature = crackcoin.ecc.verify_signature(publicKey, message, signature)

		if not signature:
			print "error1"
			return False


	totalOutputAmount = 0

	for output in transaction['outputs']:
		
		transferAmount = output['amount']
		totalOutputAmount += int(transferAmount)

		toAddress = output['address']
		newOutputHash = output['outputHash']

	# amount must be valid
	if totalOutputAmount > totalInputAmount:
		print "error5"
		return False

	# if valid, add to db
	for oldInput in transaction['inputs']:
		outputHash = oldInput['previousOutput']
		publicKey = oldInput['publicKey']
		timestamp = oldInput['timestamp']
		signature = oldInput['signature']

		crackcoin.db.doQuery(	
						"INSERT INTO transactions_inputs (previousOutput, publicKey, timestamp, signature, transactionHash) VALUES (?, ?, ?, ?, ?)", 
								(outputHash, publicKey, timestamp, signature, transactionHash), 
								result='none')

	for output in transaction['outputs']:
		transferAmount = output['amount']
		toAddress = output['address']
		newOutputHash = output['outputHash']

		crackcoin.db.doQuery(
						"INSERT INTO transactions_outputs (amount, address, outputHash, transactionHash) VALUES (?, ?, ?, ?)", 
							(str(transferAmount), toAddress, newOutputHash, transactionHash), 
							result='none')

	createTransactionConfirmation(transactionHash, transactionTimestamp)

	crackcoin.db.doQuery(
						"INSERT INTO transactions (hash, timestamp) VALUES (?, ?)", 
							(transactionHash, transactionTimestamp), 
							result='none')




def createTransaction(to, transferAmount):
	''' Try to create a transaction '''

	transferAmount = int(transferAmount)

	outputs = crackcoin.db.doQuery("select distinct transactions_outputs.amount, transactions_outputs.address, transactions_outputs.outputHash from transactions_outputs LEFT JOIN transactions_inputs WHERE NOT EXISTS(SELECT * FROM transactions_inputs WHERE transactions_outputs.outputHash = transactions_inputs.previousOutput)", result='all')
	wallets = crackcoin.db.doQuery("select * from wallets", result='all')

	for wallet in wallets:
		ID, privateKey, publicKey, myAddress = wallet
		myMoney = 0
		usedOutputs = []

		for output in outputs:
			amount, address, outputHash = output

			if address == myAddress:
				myMoney += amount
				usedOutputs.append(outputHash)

				if myMoney >= transferAmount:

					newTransactionHash = urandom(TRANSACTION_HASH_LENGTH).encode('hex')

					timestamp = str(time())

					# create inputs
					for oldOutput in usedOutputs:
						messageToSign = outputHash + publicKey + timestamp

						signature = crackcoin.ecc.sign_message(int(privateKey), messageToSign)

						correct = crackcoin.ecc.verify_signature(crackcoin.wallets.decompressPublicKey(publicKey), messageToSign, signature)
						# assert correct == True

						signature = str(signature)

						crackcoin.db.doQuery(
							"INSERT INTO transactions_inputs (previousOutput, publicKey, timestamp, signature, transactionHash) VALUES (?, ?, ?, ?, ?)", 
							(outputHash, publicKey, timestamp, signature, newTransactionHash), 
							result='none')

						inputDict = {'previousOutput':outputHash, 'publicKey':publicKey, 'timestamp':timestamp, 'signature':signature, 'transactionHash':newTransactionHash}

					# create outputs
					newOutputHash = urandom(TRANSACTION_HASH_LENGTH).encode('hex')
					crackcoin.db.doQuery(
						"INSERT INTO transactions_outputs (amount, address, outputHash, transactionHash) VALUES (?, ?, ?, ?)", 
							(str(transferAmount), to, newOutputHash, newTransactionHash), 
							result='none')
					
					outputDict = {'amount':str(transferAmount), 'address':to, 'outputHash':newOutputHash, 'transactionHash':newTransactionHash}

					if myMoney > transferAmount:
						leftOver = myMoney - transferAmount
						newOutputHash = urandom(TRANSACTION_HASH_LENGTH).encode('hex')

						crackcoin.db.doQuery(
						"INSERT INTO transactions_outputs (amount, address, outputHash, transactionHash) VALUES (?, ?, ?, ?)", 
							(leftOver, myAddress, newOutputHash, newTransactionHash), 
							result='none')

						outputDict = {'amount':str(transferAmount), 'address':to, 'outputHash':newOutputHash, 'transactionHash':newTransactionHash}

					# create transaction
					crackcoin.db.doQuery(
						"INSERT INTO transactions (hash, timestamp) VALUES (?, ?)", 
							(newTransactionHash, timestamp), 
							result='none')


					createTransactionConfirmation(newTransactionHash, timestamp)

					# send transaction and confirmation to network
					transactionJSON = getJSONForTransaction(newTransactionHash)

					crackcoin.network.broadcastTransaction(transactionJSON)

					return
							

def createTransactionConfirmation(transactionHash, timestamp):
	''' create confirmation for transaction with difficulty 1 '''

	difficulty = 1
	transactionValue = transactionHash + timestamp

	while True:

		addition = urandom(VALIDATION_ADDITION_LENGTH).encode('hex')
		solution = crackcoin.hasher(transactionValue + addition).hexdigest()

		if solution.count('0') == difficulty:

			crackcoin.network.broadcastConfirmation(transactionHash, difficulty, addition)
			crackcoin.db.doQuery('INSERT INTO confirmations (transactionHash, difficulty, addition, solution) VALUES (?, ?, ?, ?)', (transactionHash, difficulty, addition, solution), result='none')
			
			break


def addConfirmationCSV(data):
	''' Add confirmation from CSV '''

	#try:
	transactionHash, difficulty, addition = data.split(",")
	difficulty = int(difficulty)

	if len(addition) != VALIDATION_ADDITION_LENGTH: # add some validation stuffz
		return

	maxDifficulty = crackcoin.db.doQuery("select max(difficulty) from confirmations where transactionHash = ?", (transactionHash,), result='one')[0]
	
	if maxDifficulty >= difficulty:
		return
	
	timestamp = crackcoin.db.doQuery("select timestamp from transactions where hash = ?", (str(transactionHash),), result='one')[0]

	if timestamp:

		transactionValue = transactionHash + timestamp
		solution = sha512(transactionValue + addition).hexdigest()

		if solution.count('0') == difficulty:

			crackcoin.db.doQuery('DELETE FROM confirmations WHERE transactionHash = ?', (transactionHash, ), result='none')
			
			crackcoin.db.doQuery("INSERT INTO confirmations (transactionHash, difficulty, addition, solution) VALUES (?, ?, ?, ?)", (transactionHash, difficulty, addition, solution), result='none')


	#except Exception as e:
	#	print "Packet addConfirmationCSV exception"

