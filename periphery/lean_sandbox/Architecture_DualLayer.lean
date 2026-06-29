namespace Obsidia
namespace Architecture_DualLayer

structure DualLayerState where
  core_ready : Bool
  periphery_ready : Bool
  bridge_only : Bool
  kernel_authority : Bool

def core_ok (s : DualLayerState) : Prop :=
  s.core_ready = true

def periphery_ok (s : DualLayerState) : Prop :=
  s.periphery_ready = true

def bridge_only_ok (s : DualLayerState) : Prop :=
  s.bridge_only = true

def kernel_authority_ok (s : DualLayerState) : Prop :=
  s.kernel_authority = true

def dual_layer_governed (s : DualLayerState) : Prop :=
  core_ok s ∧ periphery_ok s ∧ bridge_only_ok s ∧ kernel_authority_ok s

theorem dual_layer_governed_intro
    (s : DualLayerState)
    (hc : core_ok s)
    (hp : periphery_ok s)
    (hb : bridge_only_ok s)
    (hk : kernel_authority_ok s) :
    dual_layer_governed s :=
  And.intro hc (And.intro hp (And.intro hb hk))

theorem core_from_dual_layer_governed
    (s : DualLayerState)
    (h : dual_layer_governed s) :
    core_ok s :=
  h.left

theorem periphery_from_dual_layer_governed
    (s : DualLayerState)
    (h : dual_layer_governed s) :
    periphery_ok s :=
  h.right.left

theorem bridge_only_from_dual_layer_governed
    (s : DualLayerState)
    (h : dual_layer_governed s) :
    bridge_only_ok s :=
  h.right.right.left

theorem kernel_authority_from_dual_layer_governed
    (s : DualLayerState)
    (h : dual_layer_governed s) :
    kernel_authority_ok s :=
  h.right.right.right

end Architecture_DualLayer
end Obsidia
