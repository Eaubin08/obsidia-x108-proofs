CREATE TABLE `prediction_history` (
	`id` int AUTO_INCREMENT NOT NULL,
	`predictionId` varchar(64) NOT NULL,
	`title` varchar(128) NOT NULL,
	`domain` enum('trading','bank','ecom') NOT NULL,
	`level` enum('high','medium','low') NOT NULL,
	`probability` float NOT NULL,
	`window` varchar(32) NOT NULL,
	`outcome` enum('confirmed','refuted','pending') NOT NULL DEFAULT 'pending',
	`btcVolatility` float,
	`bankRiskScore` float,
	`ecomDemandIndex` float,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`resolvedAt` timestamp,
	CONSTRAINT `prediction_history_id` PRIMARY KEY(`id`)
);
