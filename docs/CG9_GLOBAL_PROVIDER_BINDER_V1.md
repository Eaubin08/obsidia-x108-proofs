# CG9 Global Provider Binder V1


## Purpose

CG9 Global Provider Binder V1 defines the controlled integration boundary between CG9 governance and runtime providers.

Providers can execute bounded workloads.

Providers do not own decision authority.


## Architecture


CG9 Governance Layer

        |

        v

Provider Arbitration

        |

        v

Capability Arbitration

        |

        v

Invocation Envelope

        |

        v

Runtime Execution

        |

        +----------------+

        |                |

        v                v

      Brody          Obsidure

      Runtime        Runtime

        |                |

        +----------------+

                 |

                 v

          Runtime Receipt

                 |

                 v

          Conformance Proof


## Registered Providers


### Brody Runtime

Role:

- cognitive runtime execution
- bounded output generation


### Obsidure Runtime

Role:

- proof-oriented runtime execution
- verified result generation


## Governance Rules


Providers:

- cannot decide
- cannot mutate kernel
- cannot write memory
- cannot emit actions


Required invariants:


decision_authority = False

execution_authority = False

memory_write = False

kernel_mutation = False

emits_act = False


## Principle


CG9 routes and proves.

Providers execute.

KX108 retains authority.


## Status


CG9 Global Provider Binder V1 CLOSED
