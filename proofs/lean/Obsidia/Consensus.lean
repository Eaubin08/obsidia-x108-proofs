import Obsidia.Basic

namespace Obsidia

def countDec (d : Decision3) (xs : List Decision3) : Nat :=
  xs.foldl (fun acc x => if x = d then acc + 1 else acc) 0

def aggregate4 (d1 d2 d3 d4 : Decision3) : Decision3 :=
  if decide (3 <= countDec Decision3.ACT [d1, d2, d3, d4]) then
    Decision3.ACT
  else if decide (3 <= countDec Decision3.HOLD [d1, d2, d3, d4]) then
    Decision3.HOLD
  else if decide (3 <= countDec Decision3.BLOCK [d1, d2, d3, d4]) then
    Decision3.BLOCK
  else
    Decision3.BLOCK

theorem aggregate4_act
  (d1 d2 d3 d4 : Decision3)
  (h : 3 <= countDec Decision3.ACT [d1, d2, d3, d4]) :
  aggregate4 d1 d2 d3 d4 = Decision3.ACT := by
  unfold aggregate4
  have htrue : decide (3 <= countDec Decision3.ACT [d1, d2, d3, d4]) = true := decide_eq_true h
  rw [htrue]
  rfl

theorem aggregate4_fail_closed
  (d1 d2 d3 d4 : Decision3)
  (hACT : Not (3 <= countDec Decision3.ACT [d1, d2, d3, d4]))
  (hHOLD : Not (3 <= countDec Decision3.HOLD [d1, d2, d3, d4]))
  (hBLOCK : Not (3 <= countDec Decision3.BLOCK [d1, d2, d3, d4])) :
  aggregate4 d1 d2 d3 d4 = Decision3.BLOCK := by
  unfold aggregate4
  have h1 : decide (3 <= countDec Decision3.ACT [d1, d2, d3, d4]) = false := decide_eq_false hACT
  have h2 : decide (3 <= countDec Decision3.HOLD [d1, d2, d3, d4]) = false := decide_eq_false hHOLD
  have h3 : decide (3 <= countDec Decision3.BLOCK [d1, d2, d3, d4]) = false := decide_eq_false hBLOCK
  rw [h1, h2, h3]
  rfl

theorem aggregate4_unanimous
  (d : Decision3) :
  aggregate4 d d d d = d := by
  cases d <;> simp [aggregate4, countDec]

theorem no_act_and_hold_supermajority_4_aux
  (d1 d2 d3 d4 : Decision3) :
  Not (And
    (3 <= countDec Decision3.ACT [d1, d2, d3, d4])
    (3 <= countDec Decision3.HOLD [d1, d2, d3, d4])) := by
  cases d1 <;> cases d2 <;> cases d3 <;> cases d4 <;>
    decide

theorem no_act_and_block_supermajority_4_aux
  (d1 d2 d3 d4 : Decision3) :
  Not (And
    (3 <= countDec Decision3.ACT [d1, d2, d3, d4])
    (3 <= countDec Decision3.BLOCK [d1, d2, d3, d4])) := by
  cases d1 <;> cases d2 <;> cases d3 <;> cases d4 <;>
    decide

theorem no_hold_and_block_supermajority_4_aux
  (d1 d2 d3 d4 : Decision3) :
  Not (And
    (3 <= countDec Decision3.HOLD [d1, d2, d3, d4])
    (3 <= countDec Decision3.BLOCK [d1, d2, d3, d4])) := by
  cases d1 <;> cases d2 <;> cases d3 <;> cases d4 <;>
    decide

theorem no_act_and_hold_supermajority_4
  (d1 d2 d3 d4 : Decision3)
  (hAct : 3 <= countDec Decision3.ACT [d1, d2, d3, d4])
  (hHold : 3 <= countDec Decision3.HOLD [d1, d2, d3, d4]) :
  False := by
  exact no_act_and_hold_supermajority_4_aux d1 d2 d3 d4 (And.intro hAct hHold)

theorem no_act_and_block_supermajority_4
  (d1 d2 d3 d4 : Decision3)
  (hAct : 3 <= countDec Decision3.ACT [d1, d2, d3, d4])
  (hBlock : 3 <= countDec Decision3.BLOCK [d1, d2, d3, d4]) :
  False := by
  exact no_act_and_block_supermajority_4_aux d1 d2 d3 d4 (And.intro hAct hBlock)

theorem no_hold_and_block_supermajority_4
  (d1 d2 d3 d4 : Decision3)
  (hHold : 3 <= countDec Decision3.HOLD [d1, d2, d3, d4])
  (hBlock : 3 <= countDec Decision3.BLOCK [d1, d2, d3, d4]) :
  False := by
  exact no_hold_and_block_supermajority_4_aux d1 d2 d3 d4 (And.intro hHold hBlock)

theorem no_two_distinct_supermajorities_4
  (a b : Decision3) (d1 d2 d3 d4 : Decision3)
  (hab : Not (a = b))
  (ha : 3 <= countDec a [d1, d2, d3, d4])
  (hb : 3 <= countDec b [d1, d2, d3, d4]) :
  False := by
  cases a <;> cases b
  . exact (hab rfl).elim
  . exact no_hold_and_block_supermajority_4 d1 d2 d3 d4 hb ha
  . exact no_act_and_block_supermajority_4 d1 d2 d3 d4 hb ha
  . exact no_hold_and_block_supermajority_4 d1 d2 d3 d4 ha hb
  . exact (hab rfl).elim
  . exact no_act_and_hold_supermajority_4 d1 d2 d3 d4 hb ha
  . exact no_act_and_block_supermajority_4 d1 d2 d3 d4 ha hb
  . exact no_act_and_hold_supermajority_4 d1 d2 d3 d4 ha hb
  . exact (hab rfl).elim

end Obsidia

#print axioms Obsidia.no_act_and_hold_supermajority_4_aux
#print axioms Obsidia.no_act_and_block_supermajority_4_aux
#print axioms Obsidia.no_hold_and_block_supermajority_4_aux
#print axioms Obsidia.no_act_and_hold_supermajority_4
#print axioms Obsidia.no_act_and_block_supermajority_4
#print axioms Obsidia.no_hold_and_block_supermajority_4
#print axioms Obsidia.no_two_distinct_supermajorities_4