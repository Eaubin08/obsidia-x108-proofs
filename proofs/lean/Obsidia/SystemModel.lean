import Obsidia.Basic
import Obsidia.Sensitivity

namespace Obsidia.SystemModel

structure AuditRecord where
  metrics : Obsidia.Metrics
  theta   : Rat
  result  : Obsidia.Decision

structure State where
  repo     : Obsidia.Sensitivity.Repo
  auditLog : List AuditRecord

structure Input where
  metrics : Obsidia.Metrics
  theta   : Rat

def decide (i : Input) : Obsidia.Decision :=
  Obsidia.decision i.metrics i.theta

def decideInstitutional (i : Input) : Obsidia.Decision3 :=
  Obsidia.liftDecision (decide i)

theorem P17_KernelNeverBlocks (i : Input) :
    decideInstitutional i ≠ Obsidia.Decision3.BLOCK :=
  Obsidia.L11_3_no_block i.metrics i.theta

noncomputable def sealRepo (r : Obsidia.Sensitivity.Repo) : Obsidia.Hash :=
  Obsidia.Sensitivity.merkleRoot r

def transition (s : State) (i : Input) : Obsidia.Decision × State :=
  let d    := decide i
  let entry := AuditRecord.mk i.metrics i.theta d
  let s'   := State.mk s.repo (s.auditLog ++ [entry])
  (d, s')

theorem P17_Determinism (s : State) (i : Input) :
    transition s i = transition s i := rfl

theorem P17_SealSensitive
    (r r' : Obsidia.Sensitivity.Repo)
    (h : r.leaves ≠ r'.leaves) :
    sealRepo r ≠ sealRepo r' := by
  unfold sealRepo
  exact Obsidia.Sensitivity.merkleRoot_change_if_leaf_change r r' h

theorem P17_AuditLastIsComputed (s : State) (i : Input) :
    (transition s i).2.auditLog =
      s.auditLog ++ [AuditRecord.mk i.metrics i.theta (decide i)] := by
  unfold transition
  rfl

theorem auditLog_append_singleton_length
    (xs : List AuditRecord) (entry : AuditRecord) :
    (xs ++ [entry]).length = xs.length + 1 := by
  induction xs with
  | nil =>
      rfl
  | cons x xs ih =>
      simp only [List.cons_append, List.length_cons]
      rw [ih]

theorem P17_AuditGrowth (s : State) (i : Input) :
    (transition s i).2.auditLog.length = s.auditLog.length + 1 := by
  rw [P17_AuditLastIsComputed]
  exact auditLog_append_singleton_length
    s.auditLog
    (AuditRecord.mk i.metrics i.theta (decide i))

theorem P17_TransitionFstIsDecide (s : State) (i : Input) :
    (transition s i).1 = decide i := by
  unfold transition
  rfl

end Obsidia.SystemModel

#print axioms Obsidia.SystemModel.P17_AuditGrowth
#print axioms List.length_append
#print axioms List.length_singleton
#print axioms Obsidia.SystemModel.P17_AuditLastIsComputed
#print axioms Obsidia.SystemModel.P17_AuditGrowth