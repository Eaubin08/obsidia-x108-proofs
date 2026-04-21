CREATE TABLE `audit_log` (
	`id` int AUTO_INCREMENT NOT NULL,
	`ticketId` int NOT NULL,
	`hashPrev` varchar(64) NOT NULL,
	`hashNow` varchar(64) NOT NULL,
	`merkleRoot` varchar(64) NOT NULL,
	`anchorRef` varchar(128),
	`payload` json NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `audit_log_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `decision_tickets` (
	`id` int AUTO_INCREMENT NOT NULL,
	`intentId` varchar(64) NOT NULL,
	`domain` enum('trading','bank','ecom','system') NOT NULL,
	`decision` enum('ALLOW','HOLD','BLOCK') NOT NULL,
	`reasons` json NOT NULL,
	`thresholds` json NOT NULL,
	`x108` json NOT NULL,
	`auditTrail` json NOT NULL,
	`replayRef` varchar(128),
	`userId` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `decision_tickets_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `simulation_runs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`domain` enum('trading','bank','ecom') NOT NULL,
	`seed` bigint NOT NULL,
	`steps` int NOT NULL,
	`params` json NOT NULL,
	`stateHash` varchar(64) NOT NULL,
	`merkleRoot` varchar(64) NOT NULL,
	`userId` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `simulation_runs_id` PRIMARY KEY(`id`)
);
