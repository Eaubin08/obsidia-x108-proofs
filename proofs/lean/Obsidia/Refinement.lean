import Obsidia.TemporalKernel
import Obsidia.TemporalX108

namespace Obsidia
namespace Refinement

/--
Refinement bridge.

This file intentionally does not introduce a new sovereign decision function.
It re-exports the current TemporalKernel/X108 safety facts under the Refinement layer.
The old names `decideX108` and `decide3X108` were stale references and are not recreated here.
-/
def refinement_X108_no_act_before_tau :=
  Obsidia.TemporalKernel.X108_no_act_before_tau

def refinement_X108_after_tau_equals_base :=
  Obsidia.TemporalKernel.X108_after_tau_equals_base

def refinement_X108_kernel_never_blocks :=
  Obsidia.TemporalKernel.X108_kernel_never_blocks

def refinement_X108_reversible_equals_base :=
  Obsidia.TemporalKernel.X108_reversible_equals_base

def refinement_X108_irreversible_after_tau_equals_base :=
  Obsidia.TemporalKernel.X108_irreversible_after_tau_equals_base

end Refinement
end Obsidia
