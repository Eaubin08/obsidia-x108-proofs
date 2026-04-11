/**
 * Shared Constants
 * Used across server and client
 */

// Auth
export const COOKIE_NAME = "session";
export const NOT_ADMIN_ERR_MSG = "Not an admin";
export const UNAUTHED_ERR_MSG = "Unauthorized";

// Time
export const ONE_YEAR_MS = 365 * 24 * 60 * 60 * 1000;

// API
export const AXIOS_TIMEOUT_MS = 30000; // 30 seconds

// Routes
export const ADMIN_ONLY_ROUTES = ["/admin", "/dashboard"];
export const PUBLIC_ROUTES = ["/", "/login", "/signup"];

// Errors
export const ERROR_MESSAGES = {
  UNAUTHORIZED: "Unauthorized",
  FORBIDDEN: "Forbidden",
  NOT_FOUND: "Not found",
  BAD_REQUEST: "Bad request",
  INTERNAL_ERROR: "Internal server error",
} as const;
