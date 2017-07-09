BEGIN TRANSACTION;
CREATE TABLE `wallets` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`privateKey`	TEXT,
	`publicKey`	TEXT,
	`address`	TEXT
);
CREATE TABLE "transactions_outputs" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`amount`	INTEGER,
	`address`	TEXT,
	`outputHash`	TEXT,
	`transactionHash`	TEXT
);
INSERT INTO `transactions_outputs` (id,amount,address,outputHash,transactionHash) VALUES (1,31337,'crackcoint3wMFeUjEyrNMRjUR3Y8wm2LopaQmy3PRjaKyWceN','7b50615376ca368b16414deef71e2016f10eda31f4287e041286fcae76fa80fb','d34db33f');
CREATE TABLE "transactions_inputs" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`previousOutput`	TEXT,
	`publicKey`	TEXT,
	`timestamp`	TEXT,
	`signature`	TEXT,
	`transactionHash`	TEXT
);
INSERT INTO `transactions_inputs` (id,previousOutput,publicKey,timestamp,signature,transactionHash) VALUES (1,'foo','b4r','123213123213','foobar','d34db33f');
CREATE TABLE "transactions" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`hash`	TEXT,
	`timestamp`	TEXT
);
INSERT INTO `transactions` (id,hash,timestamp) VALUES (1,'d34db33f','1478448432.959781');
CREATE TABLE `confirmations` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`transactionHash`	TEXT,
	`difficulty`	INTEGER,
	`addition`	TEXT,
	`solution`	TEXT
);
INSERT INTO `confirmations` (id,transactionHash,difficulty,addition,solution) VALUES (67,'d34db33f',6,'290b700cc485b496798357d94ca4ef169b4b22a6','40fee3da41f99effaaa368e65052d03af1e28ec9bebdd13e468f9854e42b4da1ce4c23d9d42b9c28020588fe121908364caf4b441f79a5f33d6c36c5dac1a5d1');
COMMIT;
