import Obsidia.Basic
import Obsidia.TemporalX108
import Obsidia.Refinement
import Obsidia.Consensus
import Obsidia.SystemModel
import Obsidia.Sensitivity
import Obsidia.Seal
import Obsidia.Merkle
import Obsidia.CryptoAssumptions

#print axioms Obsidia.decision_eq_ACT_iff
#print axioms Obsidia.decision_eq_HOLD_iff
#print axioms Obsidia.L11_3_no_block

#print axioms Obsidia.X108_after_tau_equals_base
#print axioms Obsidia.X108_kernel_never_blocks
#print axioms Obsidia.X108_no_act_before_tau
#print axioms Obsidia.X108_reversible_equals_base
#print axioms Obsidia.X108_irreversible_after_tau_equals_base

#print axioms Obsidia.Refinement.lift_refines
#print axioms Obsidia.Refinement.x108_never_blocks

#print axioms Obsidia.aggregate4_act
#print axioms Obsidia.aggregate4_fail_closed
#print axioms Obsidia.aggregate4_unanimous
#print axioms Obsidia.no_two_distinct_supermajorities_4

#print axioms Obsidia.SystemModel.P17_AuditGrowth

#print axioms Obsidia.foldl_H_injective
#print axioms Obsidia.merkle2_right_mutation
#print axioms Obsidia.SealAssumptions.combine_inj
#print axioms Obsidia.Sensitivity.merkleRoot_change_if_leaf_change
#print axioms Obsidia.Sensitivity.P15_Immutability_Strong
#print axioms Obsidia.Seal.P13_Immutability
