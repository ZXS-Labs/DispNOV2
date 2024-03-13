from models.gwcnet_pianchaHorizonDef import GwcNet_GC
from models.gwcnet_pianchaHorizonDefDispNONoGar import GwcNet_GC_DispNO_NoGar
from models.gwcnet_pianchaHorizonDefDispNOCostGar import GwcNet_GC_DispNO_CostGar
from models.gwcnet_pianchaHorizonDefDispNO import GwcNet_GC_DispNO
from models.gwcnet_pianchaHorizonDefDispNORange import GwcNet_GC_DispNO_Range
from models.loss import model_loss, unimodal_loss, bimodal_loss

__models__ = {
    "gwcnet-gc": GwcNet_GC,
    "gwcnet-gc-dispno-noGar": GwcNet_GC_DispNO_NoGar,
    "gwcnet-gc-dispno-costGar": GwcNet_GC_DispNO_CostGar,
    "gwcnet-gc-dispno": GwcNet_GC_DispNO,
    "gwcnet-gc-dispno-range": GwcNet_GC_DispNO_Range,
}
