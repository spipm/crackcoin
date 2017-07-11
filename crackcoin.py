#!/usr/bin/python

import crackcoin

import crackcoin.wallets
import crackcoin.transactions


commands = {'q':'quit', 'h':'help', 'b':'broadcast', 't':'transaction', 'i':'information'}
running = True

if __name__ == "__main__":

	crackcoin.network.startNetworking()
	crackcoin.miner.startMining()
	
	while running:

		try:
		
			ui = raw_input("> ")

			if ui == 'q':
				break

			if ui == 'h':
				for c in commands:
					print "%s: %s" % (c, commands[c])

			if ui == 't':
				to = raw_input("To: ")
				amount = raw_input("Amount: ")
				crackcoin.transactions.createTransaction(to, amount)

			if ui == 'i':
				crackcoin.wallets.printBasicInfo()

			if ui == 'b':
				crackcoin.network.broadcastSync()

		except KeyboardInterrupt:
			print "Exiting ..."
			running = False
			break
				
		except Exception as e:
			print "Exception in main: " + e.message
			break

	crackcoin.network.stopServer = True
	crackcoin.miner.stopMiner = True
	crackcoin.threader.waitForThreads()
