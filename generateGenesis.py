#!/usr/bin/python

import crackcoin

import crackcoin.wallets
import crackcoin.transactions

#coolAddressNames = ['crackcoin','crackcoiN','crackco1n','crackco1N']

#while 1:
privateKey, publicKey = crackcoin.wallets.crackcoin.ecc.make_keypair()
compressedPublicKey  = crackcoin.wallets.compressPublicKey(publicKey)
newAddress = crackcoin.wallets.publicKeyToAddress(compressedPublicKey)

#print newAddress[:9]
#if newAddress[:9] in coolAddressNames:
print "Private key:\n\t%s" % privateKey
#print publicKey
print "Compressed public key:\n\t%s" % compressedPublicKey
print "Address:\n\t%s" % newAddress
