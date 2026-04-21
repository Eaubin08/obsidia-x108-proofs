ALTER TABLE `portfolio_snapshots` ADD `domain` enum('trading','bank','ecom') DEFAULT 'trading';--> statement-breakpoint
ALTER TABLE `portfolio_snapshots` ADD `scenarioName` varchar(128);