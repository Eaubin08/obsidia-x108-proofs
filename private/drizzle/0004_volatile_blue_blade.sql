CREATE TABLE `prediction_snapshots` (
	`id` int AUTO_INCREMENT NOT NULL,
	`domain` enum('trading','bank','ecom') NOT NULL,
	`predictionId` varchar(64) NOT NULL,
	`probability` int NOT NULL,
	`btcVolatility` float,
	`bankRiskScore` float,
	`ecomDemandIndex` float,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `prediction_snapshots_id` PRIMARY KEY(`id`)
);
