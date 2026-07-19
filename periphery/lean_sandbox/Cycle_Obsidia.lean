namespace Obsidia
namespace Cycle_Obsidia

inductive ObsidianCycleStage where
  | spark
  | friction
  | readjustment
  | calibration
  | provisional_stabilisation
deriving DecidableEq

def next_stage (s : ObsidianCycleStage) : ObsidianCycleStage :=
  match s with
  | ObsidianCycleStage.spark => ObsidianCycleStage.friction
  | ObsidianCycleStage.friction => ObsidianCycleStage.readjustment
  | ObsidianCycleStage.readjustment => ObsidianCycleStage.calibration
  | ObsidianCycleStage.calibration => ObsidianCycleStage.provisional_stabilisation
  | ObsidianCycleStage.provisional_stabilisation => ObsidianCycleStage.spark

structure ObsidianCycleState where
  spark_ready : Bool
  friction_present : Bool
  readjustment_ready : Bool
  calibration_ready : Bool
  stabilisation_ready : Bool
  new_spark_ready : Bool

def spark_active (s : ObsidianCycleState) : Prop :=
  s.spark_ready = true

def friction_active (s : ObsidianCycleState) : Prop :=
  s.friction_present = true

def readjustment_active (s : ObsidianCycleState) : Prop :=
  s.readjustment_ready = true

def calibration_active (s : ObsidianCycleState) : Prop :=
  s.calibration_ready = true

def stabilisation_active (s : ObsidianCycleState) : Prop :=
  s.stabilisation_ready = true

def new_spark_active (s : ObsidianCycleState) : Prop :=
  s.new_spark_ready = true

def obsidian_cycle_complete (s : ObsidianCycleState) : Prop :=
  And (spark_active s)
    (And (friction_active s)
      (And (readjustment_active s)
        (And (calibration_active s)
          (And (stabilisation_active s) (new_spark_active s)))))

def canonical_obsidian_cycle_state : ObsidianCycleState :=
  { spark_ready := true,
    friction_present := true,
    readjustment_ready := true,
    calibration_ready := true,
    stabilisation_ready := true,
    new_spark_ready := true }

theorem next_after_spark :
    next_stage ObsidianCycleStage.spark = ObsidianCycleStage.friction :=
  rfl

theorem next_after_friction :
    next_stage ObsidianCycleStage.friction = ObsidianCycleStage.readjustment :=
  rfl

theorem next_after_readjustment :
    next_stage ObsidianCycleStage.readjustment = ObsidianCycleStage.calibration :=
  rfl

theorem next_after_calibration :
    next_stage ObsidianCycleStage.calibration = ObsidianCycleStage.provisional_stabilisation :=
  rfl

theorem next_after_stabilisation :
    next_stage ObsidianCycleStage.provisional_stabilisation = ObsidianCycleStage.spark :=
  rfl

theorem obsidian_cycle_complete_intro
    (s : ObsidianCycleState)
    (hs : spark_active s)
    (hf : friction_active s)
    (hr : readjustment_active s)
    (hc : calibration_active s)
    (ht : stabilisation_active s)
    (hn : new_spark_active s) :
    obsidian_cycle_complete s :=
  And.intro hs
    (And.intro hf
      (And.intro hr
        (And.intro hc
          (And.intro ht hn))))

theorem spark_from_obsidian_cycle
    (s : ObsidianCycleState)
    (h : obsidian_cycle_complete s) :
    spark_active s :=
  h.left

theorem friction_from_obsidian_cycle
    (s : ObsidianCycleState)
    (h : obsidian_cycle_complete s) :
    friction_active s :=
  h.right.left

theorem readjustment_from_obsidian_cycle
    (s : ObsidianCycleState)
    (h : obsidian_cycle_complete s) :
    readjustment_active s :=
  h.right.right.left

theorem calibration_from_obsidian_cycle
    (s : ObsidianCycleState)
    (h : obsidian_cycle_complete s) :
    calibration_active s :=
  h.right.right.right.left

theorem stabilisation_from_obsidian_cycle
    (s : ObsidianCycleState)
    (h : obsidian_cycle_complete s) :
    stabilisation_active s :=
  h.right.right.right.right.left

theorem new_spark_from_obsidian_cycle
    (s : ObsidianCycleState)
    (h : obsidian_cycle_complete s) :
    new_spark_active s :=
  h.right.right.right.right.right

theorem canonical_obsidian_cycle_complete :
    obsidian_cycle_complete canonical_obsidian_cycle_state :=
  And.intro rfl
    (And.intro rfl
      (And.intro rfl
        (And.intro rfl
          (And.intro rfl rfl))))

end Cycle_Obsidia
end Obsidia
