import Lake
open Lake DSL

package "obsidia-engine-proof-core" where
  lean_lib Obsidia

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.28.0"