/**
 * TLA+ Verification Configuration
 * Gère les variables d'environnement et la validation config pour TLA
 */

export interface TLAConfig {
  enabled: boolean;
  tlc_cmd: string | null;
  timeout: number;
  tla_root: string | null;
}

export function getTLAConfig(): TLAConfig {
  const enabled = process.env.OBSIDIA_TLA_ENABLED === "true";
  const tlc_cmd = process.env.OBSIDIA_TLA_TLC_CMD || null;
  const timeout = parseInt(process.env.OBSIDIA_TLA_TIMEOUT || "60000", 10);
  const tla_root = process.env.OBSIDIA_TLA_ROOT || null;

  return {
    enabled,
    tlc_cmd,
    timeout,
    tla_root,
  };
}

export function validateTLAConfig(config: TLAConfig): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (config.enabled && !config.tlc_cmd) {
    errors.push("OBSIDIA_TLA_ENABLED=true but OBSIDIA_TLA_TLC_CMD not set");
  }

  if (config.timeout < 5000) {
    errors.push("OBSIDIA_TLA_TIMEOUT must be >= 5000ms");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
