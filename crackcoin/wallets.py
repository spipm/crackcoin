import crackcoin

wallet_prefix = "crack"


def publicKeyToAddress(compressedPublicKey):
	''' Generate address from public key '''

	h = crackcoin.hasher(compressedPublicKey).digest()
	return wallet_prefix + "c" + crackcoin.encoder.b58encode(h)

def createNewWallet():
	''' Create wallet and save in db '''

	privateKey, publicKey = crackcoin.ecc.make_keypair()
	compressedPublicKey  = compressPublicKey(publicKey)
	newAddress = publicKeyToAddress(compressedPublicKey)
	crackcoin.db.doQuery('INSERT INTO wallets (privateKey, publicKey, address) VALUES (?, ?, ?)', (str(privateKey), str(compressedPublicKey), newAddress), result='none')


def printBasicInfo():
	''' Print basic wallet info '''

	outputs = crackcoin.db.doQuery("select distinct transactions_outputs.amount, transactions_outputs.address, transactions_outputs.outputHash from transactions_outputs LEFT JOIN transactions_inputs WHERE NOT EXISTS(SELECT * FROM transactions_inputs WHERE transactions_outputs.outputHash = transactions_inputs.previousOutput)", result='all')
	wallets = crackcoin.db.doQuery("select * from wallets", result='all')

	totalMoney = 0

	for wallet in wallets:
		ID, privateKey, publicKey, myAddress = wallet

		print "Wallet address: %s " % myAddress

		walletMoney = 0
		for output in outputs:
			amount, address, outputHash = output

			if address == myAddress:
				walletMoney += amount

		print "Money in wallet: %s\n" % str(walletMoney)
		totalMoney += walletMoney

	print "Total money: %s\n" % str(totalMoney)


def compressPublicKey(publicKey):
	''' Compress public key '''

	compressedPublicKey = wallet_prefix
	p = crackcoin.ecc.p

	x = publicKey[0]
	ysquared = ((x*x*x+7) % p)
	y1 = pow(ysquared, (p+1)/4, p)
	y2 = y1 * -1 % p

	if y2 == publicKey[1]:
	    compressedPublicKey += "p"
	else:
	    compressedPublicKey += "m"

	a = hex(x)[2:].rstrip('L')
	if len(a)%2 == 1:
	    a = '0' + a
	a = a.decode('hex')

	compressedPublicKey += crackcoin.encoder.b58encode(a)
	return compressedPublicKey

def decompressPublicKey(compressedPublicKey):
	''' Decompress public key '''

	p = crackcoin.ecc.p

	x = int(crackcoin.encoder.b58decode(compressedPublicKey[len(wallet_prefix)+1:]).encode('hex'),16)
	ysquared = ((x*x*x+7) % p)
	y = pow(ysquared, (p+1)/4, p)

	if compressedPublicKey[len(wallet_prefix)] == 'p':
	    y = y * -1 % p

	return (x,y)



