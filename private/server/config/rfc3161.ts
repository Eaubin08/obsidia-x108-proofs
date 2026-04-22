/**
 * RFC3161 TSA Configuration
 * Gère les variables d'environnement et la validation config pour RFC3161
 */

export interface RFC3161Config {
  enabled: boolean;
  tsa_url: string | null;
  ca_cert: string | null;
  timeout: number;
}

export function getRFC3161Config(): RFC3161Config {
  const enabled = process.env.OBSIDIA_RFC3161_ENABLED === "true";
  const tsa_url = process.env.OBSIDIA_TSA_URL || null;
  const ca_cert = process.env.OBSIDIA_TSA_CA_CERT || null;
  const timeout = parseInt(process.env.OBSIDIA_TSA_TIMEOUT || "30000", 10);

  return {
    enabled,
    tsa_url,
    ca_cert,
    timeout,
  };
}

export function validateRFC3161Config(config: RFC3161Config): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (config.enabled && !config.tsa_url) {
    errors.push("OBSIDIA_RFC3161_ENABLED=true but OBSIDIA_TSA_URL not set");
  }

  if (config.timeout < 1000) {
    errors.push("OBSIDIA_TSA_TIMEOUT must be >= 1000ms");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
