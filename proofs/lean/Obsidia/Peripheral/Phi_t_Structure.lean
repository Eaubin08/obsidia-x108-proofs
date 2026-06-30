namespace Obsidia
namespace PhiTStructure

structure PhiEdge where
source : Nat
target : Nat
weight : Nat

structure PhiGraph where
main_edge : PhiEdge
stability : Nat
coherence : Nat

def edge_source (e : PhiEdge) : Nat :=
e.source

def edge_target (e : PhiEdge) : Nat :=
e.target

def edge_weight (e : PhiEdge) : Nat :=
e.weight

def graph_stability (g : PhiGraph) : Nat :=
g.stability

def graph_coherence (g : PhiGraph) : Nat :=
g.coherence

def tension (g : PhiGraph) : Nat :=
edge_weight g.main_edge

def coherent_graph (g : PhiGraph) : Prop :=
graph_coherence g <= graph_stability g

def stable_phi (g : PhiGraph) : Prop :=
coherent_graph g

theorem edge_source_reflects_field
(e : PhiEdge) :
edge_source e = e.source :=
rfl

theorem edge_target_reflects_field
(e : PhiEdge) :
edge_target e = e.target :=
rfl

theorem edge_weight_reflects_field
(e : PhiEdge) :
edge_weight e = e.weight :=
rfl

theorem tension_reflects_main_edge_weight
(g : PhiGraph) :
tension g = g.main_edge.weight :=
rfl

theorem coherent_graph_intro
(g : PhiGraph)
(h : graph_coherence g <= graph_stability g) :
coherent_graph g :=
h

theorem stable_phi_intro
(g : PhiGraph)
(h : coherent_graph g) :
stable_phi g :=
h

theorem coherent_graph_from_stable_phi
(g : PhiGraph)
(h : stable_phi g) :
coherent_graph g :=
h

end PhiTStructure
end Obsidia
