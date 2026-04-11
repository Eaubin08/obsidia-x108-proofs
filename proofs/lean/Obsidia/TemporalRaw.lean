import Obsidia.Basic

namespace Obsidia
namespace TemporalRaw

structure TInput_Raw where
  metrics   : Metrics
  theta     : Rat
  irr       : Bool
  createdAt : Int
  now       : Int

def elapsed_raw (i : TInput_Raw) : Int :=
  i.now - i.createdAt

end TemporalRaw
end Obsidia
