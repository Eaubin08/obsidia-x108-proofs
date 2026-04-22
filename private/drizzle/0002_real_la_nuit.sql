CREATE TABLE `portfolio_snapshots` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`capital` float NOT NULL,
	`pnl` float NOT NULL,
	`guardBlocks` int NOT NULL,
	`capitalSaved` float NOT NULL,
	`snapshotAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `portfolio_snapshots_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `positions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`domain` enum('trading','bank','ecom') NOT NULL,
	`asset` varchar(32) NOT NULL,
	`quantity` float NOT NULL DEFAULT 0,
	`avgEntryPrice` float NOT NULL DEFAULT 0,
	`currentValue` float NOT NULL DEFAULT 0,
	`unrealizedPnl` float NOT NULL DEFAULT 0,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `positions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `wallets` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`capital` float NOT NULL DEFAULT 125000,
	`pnl24h` float NOT NULL DEFAULT 0,
	`pnl24hPct` float NOT NULL DEFAULT 0,
	`guardBlocks` int NOT NULL DEFAULT 0,
	`capitalSaved` float NOT NULL DEFAULT 0,
	`bankBalance` float NOT NULL DEFAULT 125000,
	`bankLiquidity` float NOT NULL DEFAULT 0.82,
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `wallets_id` PRIMARY KEY(`id`),
	CONSTRAINT `wallets_userId_unique` UNIQUE(`userId`)
);
