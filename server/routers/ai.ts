import { z } from "zod/v4";
import { publicProcedure, router } from "../_core/trpc";
import { invokeLLM } from "../_core/llm";

export const aiRouter = router({
  /**
   * Traducteur IA — explique une décision X-108 en langage novice
   */
  explainDecision: publicProcedure
    .input(
      z.object({
        vertical: z.enum(["TRADING", "BANK", "ECOM"]),
        decision: z.enum(["ALLOW", "HOLD", "BLOCK"]),
        metrics: z.record(z.string(), z.number()),
        context: z.string().optional(),
        capitalImpact: z.number().optional(),
      })
    )
    .mutation(async ({ input }) => {
      const { vertical, decision, metrics, context, capitalImpact } = input;

      const metricsStr = Object.entries(metrics)
        .map(([k, v]) => `${k}: ${typeof v === "number" ? v.toFixed(3) : v}`)
        .join(", ");

      const capitalStr = capitalImpact
        ? `Capital protégé/impacté : ${capitalImpact > 0 ? "+" : ""}${capitalImpact.toLocaleString("fr-FR")} €`
        : "";

      const systemPrompt = `Tu es un traducteur pédagogique pour la plateforme OS4 (Obsidia Governance Platform).
Tu expliques les décisions du moteur Guard X-108 en langage simple, compréhensible par un novice complet.
Ton explication doit :
- Être en français, courte (2-3 phrases max)
- Commencer par ce qui s'est passé concrètement (ex: "Paiement refusé.", "Transaction autorisée.", "Décision suspendue.")
- Expliquer pourquoi en termes simples (pas de jargon technique)
- Si applicable, mentionner l'impact financier
- Être rassurante et éducative, pas alarmiste
Réponds UNIQUEMENT avec l'explication, sans titre ni formatage.`;

      const userPrompt = `Verticale : ${vertical}
Décision X-108 : ${decision}
Métriques : ${metricsStr}
${context ? `Contexte : ${context}` : ""}
${capitalStr}`;

      try {
        const response = await invokeLLM({
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt },
          ],
        });

        const explanation =
          (typeof response?.choices?.[0]?.message?.content === 'string' ? response.choices[0].message.content.trim() : null) ||
          fallbackExplanation(vertical, decision, capitalImpact);

        return { explanation, ok: true };
      } catch {
        return {
          explanation: fallbackExplanation(vertical, decision, capitalImpact),
          ok: false,
        };
      }
    }),
});

function fallbackExplanation(
  vertical: string,
  decision: string,
  capitalImpact?: number
): string {
  const capitalStr =
    capitalImpact && capitalImpact > 0
      ? ` Capital protégé : +${capitalImpact.toLocaleString("fr-FR")} €.`
      : "";

  if (decision === "BLOCK") {
    if (vertical === "BANK")
      return `Paiement refusé. Ce bénéficiaire est inhabituel et le niveau de risque dépasse le seuil de sécurité.${capitalStr}`;
    if (vertical === "ECOM")
      return `Action de l'agent bloquée. Une incohérence structurelle a été détectée — dépenser du budget pub sans stock disponible est une erreur.${capitalStr}`;
    return `Opération bloquée. Le moteur Guard X-108 a détecté une anomalie critique.${capitalStr}`;
  }
  if (decision === "HOLD") {
    return `Décision suspendue. Le système attend ${10} secondes pour s'assurer que cette action irréversible est bien intentionnelle. C'est une mesure de sécurité normale.`;
  }
  return `Opération autorisée. Tous les critères de sécurité sont satisfaits.${capitalStr}`;
}
