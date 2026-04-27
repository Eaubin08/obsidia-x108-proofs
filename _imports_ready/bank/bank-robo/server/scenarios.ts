/**
 * Bank Safety Lab - Transaction Scenarios
 * 23 scenarios: 19 AUTORISER, 3 ANALYSER, 1 BLOQUER
 */

export interface Scenario {
  name: string;
  expectedDecision: "AUTORISER" | "ANALYSER" | "BLOQUER";
  description: string;
  // Sensor values (0-1 range)
  sensors: {
    amount: number; // Montant normalisé
    frequency: number; // Fréquence des transactions
    location: number; // Distance géographique
    timeOfDay: number; // Heure de la journée
    accountAge: number; // Âge du compte
  };
}

export const SCENARIOS: Scenario[] = [
  // ===== 19 AUTORISER =====
  {
    name: "Client-Premium",
    expectedDecision: "AUTORISER",
    description: "Client premium avec historique excellent",
    sensors: { amount: 0.3, frequency: 0.2, location: 0.1, timeOfDay: 0.5, accountAge: 0.9 },
  },
  {
    name: "Achat-Regulier",
    expectedDecision: "AUTORISER",
    description: "Achat régulier dans commerce habituel",
    sensors: { amount: 0.2, frequency: 0.3, location: 0.05, timeOfDay: 0.6, accountAge: 0.7 },
  },
  {
    name: "Virement-Famille",
    expectedDecision: "AUTORISER",
    description: "Virement vers membre de la famille",
    sensors: { amount: 0.4, frequency: 0.4, location: 0.2, timeOfDay: 0.7, accountAge: 0.8 },
  },
  {
    name: "Paiement-Facture",
    expectedDecision: "AUTORISER",
    description: "Paiement de facture récurrente",
    sensors: { amount: 0.25, frequency: 0.1, location: 0.0, timeOfDay: 0.4, accountAge: 0.85 },
  },
  {
    name: "Retrait-ATM-Habituel",
    expectedDecision: "AUTORISER",
    description: "Retrait ATM dans zone habituelle",
    sensors: { amount: 0.15, frequency: 0.35, location: 0.08, timeOfDay: 0.55, accountAge: 0.75 },
  },
  {
    name: "Achat-En-Ligne-Connu",
    expectedDecision: "AUTORISER",
    description: "Achat en ligne sur site connu",
    sensors: { amount: 0.35, frequency: 0.25, location: 0.15, timeOfDay: 0.65, accountAge: 0.8 },
  },
  {
    name: "Virement-Salaire",
    expectedDecision: "AUTORISER",
    description: "Réception de salaire mensuel",
    sensors: { amount: 0.8, frequency: 0.05, location: 0.0, timeOfDay: 0.3, accountAge: 0.9 },
  },
  {
    name: "Paiement-Restaurant",
    expectedDecision: "AUTORISER",
    description: "Paiement dans restaurant local",
    sensors: { amount: 0.12, frequency: 0.4, location: 0.12, timeOfDay: 0.75, accountAge: 0.7 },
  },
  {
    name: "Achat-Supermarche",
    expectedDecision: "AUTORISER",
    description: "Achat au supermarché habituel",
    sensors: { amount: 0.18, frequency: 0.45, location: 0.06, timeOfDay: 0.68, accountAge: 0.82 },
  },
  {
    name: "Virement-Epargne",
    expectedDecision: "AUTORISER",
    description: "Virement vers compte épargne",
    sensors: { amount: 0.5, frequency: 0.15, location: 0.0, timeOfDay: 0.5, accountAge: 0.88 },
  },
  {
    name: "Paiement-Abonnement",
    expectedDecision: "AUTORISER",
    description: "Paiement d'abonnement mensuel",
    sensors: { amount: 0.08, frequency: 0.05, location: 0.0, timeOfDay: 0.2, accountAge: 0.9 },
  },
  {
    name: "Achat-Pharmacie",
    expectedDecision: "AUTORISER",
    description: "Achat en pharmacie locale",
    sensors: { amount: 0.1, frequency: 0.3, location: 0.1, timeOfDay: 0.6, accountAge: 0.75 },
  },
  {
    name: "Virement-Loyer",
    expectedDecision: "AUTORISER",
    description: "Paiement du loyer mensuel",
    sensors: { amount: 0.7, frequency: 0.05, location: 0.0, timeOfDay: 0.25, accountAge: 0.85 },
  },
  {
    name: "Paiement-Essence",
    expectedDecision: "AUTORISER",
    description: "Paiement à la station-service",
    sensors: { amount: 0.22, frequency: 0.38, location: 0.18, timeOfDay: 0.58, accountAge: 0.78 },
  },
  {
    name: "Achat-Vetements",
    expectedDecision: "AUTORISER",
    description: "Achat dans magasin de vêtements",
    sensors: { amount: 0.42, frequency: 0.12, location: 0.25, timeOfDay: 0.72, accountAge: 0.72 },
  },
  {
    name: "Virement-Cadeau",
    expectedDecision: "AUTORISER",
    description: "Virement cadeau vers contact connu",
    sensors: { amount: 0.28, frequency: 0.08, location: 0.3, timeOfDay: 0.65, accountAge: 0.8 },
  },
  {
    name: "Paiement-Parking",
    expectedDecision: "AUTORISER",
    description: "Paiement de parking",
    sensors: { amount: 0.05, frequency: 0.5, location: 0.22, timeOfDay: 0.48, accountAge: 0.7 },
  },
  {
    name: "Achat-Librairie",
    expectedDecision: "AUTORISER",
    description: "Achat en librairie",
    sensors: { amount: 0.16, frequency: 0.18, location: 0.15, timeOfDay: 0.62, accountAge: 0.76 },
  },
  {
    name: "Virement-Remboursement",
    expectedDecision: "AUTORISER",
    description: "Remboursement entre amis",
    sensors: { amount: 0.32, frequency: 0.22, location: 0.2, timeOfDay: 0.7, accountAge: 0.74 },
  },

  // ===== 3 ANALYSER =====
  {
    name: "Achat-Montant-Eleve",
    expectedDecision: "ANALYSER",
    description: "Achat d'un montant inhabituel",
    sensors: { amount: 0.85, frequency: 0.02, location: 0.4, timeOfDay: 0.35, accountAge: 0.6 },
  },
  {
    name: "Virement-Nouveau-Beneficiaire",
    expectedDecision: "ANALYSER",
    description: "Virement vers nouveau bénéficiaire",
    sensors: { amount: 0.6, frequency: 0.01, location: 0.5, timeOfDay: 0.8, accountAge: 0.5 },
  },
  {
    name: "Retrait-ATM-Etranger",
    expectedDecision: "ANALYSER",
    description: "Retrait ATM dans pays étranger",
    sensors: { amount: 0.45, frequency: 0.01, location: 0.9, timeOfDay: 0.15, accountAge: 0.65 },
  },

  // ===== 1 BLOQUER =====
  {
    name: "Transaction-Suspecte",
    expectedDecision: "BLOQUER",
    description: "Transaction hautement suspecte",
    sensors: { amount: 0.95, frequency: 0.95, location: 0.95, timeOfDay: 0.05, accountAge: 0.1 },
  },
];

/**
 * Get a random scenario from the list
 */
export function getRandomScenario(): Scenario {
  return SCENARIOS[Math.floor(Math.random() * SCENARIOS.length)]!;
}

/**
 * Get scenario by name
 */
export function getScenarioByName(name: string): Scenario | undefined {
  return SCENARIOS.find((s) => s.name === name);
}
