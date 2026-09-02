"""
CG15 KX108 Context Calibration Receipt V1
"""

from dataclasses import dataclass


@dataclass
class KX108ContextCalibrationReceipt:

    receipt_id: str
    context_id: str
    calibration_target: str
    calibration_status: str
    kernel_mutation: bool


    def to_dict(self):

        return {
            "receipt_id": self.receipt_id,
            "context_id": self.context_id,
            "calibration_target": self.calibration_target,
            "calibration_status": self.calibration_status,
            "kernel_mutation": self.kernel_mutation,
        }


class KX108ContextCalibrationReceiptBuilder:


    def __init__(self):

        self.memory_write = False
        self.kernel_mutation = False


    def create(
        self,
        context: dict,
        calibration: dict,
    ):

        return KX108ContextCalibrationReceipt(

            receipt_id=
                "kx108-context-calibration-receipt-v1",

            context_id=
                context.get(
                    "context_id",
                    "unknown",
                ),

            calibration_target=
                "PERIPHERY",

            calibration_status=
                calibration.get(
                    "status",
                    "APPLIED",
                ),

            kernel_mutation=False,
        )


    def status(self):

        return {
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
