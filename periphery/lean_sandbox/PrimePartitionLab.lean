namespace Obsidia
namespace PrimePartitionLab

structure Partition where
  left : Nat
  right : Nat
  total : Nat

def partition_ok (p : Partition) : Prop :=
  p.left + p.right = p.total

def balanced (p : Partition) : Prop :=
  p.left <= p.total ∧ p.right <= p.total

def admissible_partition (p : Partition) : Prop :=
  partition_ok p ∧ balanced p

theorem admissible_partition_intro
    (p : Partition)
    (h0 : partition_ok p)
    (h1 : balanced p) :
    admissible_partition p :=
  And.intro h0 h1

theorem partition_ok_from_admissible
    (p : Partition)
    (h : admissible_partition p) :
    partition_ok p :=
  h.left

theorem balanced_from_admissible
    (p : Partition)
    (h : admissible_partition p) :
    balanced p :=
  h.right

end PrimePartitionLab
end Obsidia