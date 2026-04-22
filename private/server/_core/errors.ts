export class ForbiddenError extends Error {
  status = 403;
  statusCode = 403;

  constructor(message = "Forbidden") {
    super(message);
    this.name = "ForbiddenError";
  }
}
