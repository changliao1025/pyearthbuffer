"""Case management for pyearthbuffer operations."""

import datetime
import json
import os
from json import JSONEncoder
from pathlib import Path
from typing import Any, Optional

import numpy as np
from pyearth.toolbox.date.timer import pytimer


class CaseClassEncoder(JSONEncoder):
    """JSON encoder that handles NumPy scalar and array types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class pycase:
    """The pyearthbuffer case class for managing buffer operations.

    Args:
        aConfig_in (Dict[str, Any]): A dictionary of configuration parameters.
        sDate_in (Optional[str], optional): The case date string. Defaults to None.
        sWorkspace_output_in (Optional[str], optional): The output workspace path. Defaults to None.
    """

    iCase_index: int = 0
    sCase: str = ""
    sDate: str = ""
    sWorkspace_output: str = ""

    def __init__(
        self,
        aConfig_in: dict[str, Any],
        sDate_in: Optional[str] = None,
        sWorkspace_output_in: Optional[str] = None,
    ):
        # Set case index
        iCase_index = int(aConfig_in.get("iCase_index", 1))
        self.iCase_index = iCase_index
        sCase_index = f"{iCase_index:03d}"

        # Set date
        pDate = datetime.datetime.today()
        sDate_default = f"{pDate.year:04d}{pDate.month:02d}{pDate.day:02d}"

        if sDate_in is not None:
            self.sDate = sDate_in
        elif "sDate" in aConfig_in:
            self.sDate = aConfig_in["sDate"]
        else:
            self.sDate = sDate_default

        # Set case name
        sModel = aConfig_in.get("sModel", "pyearthbuffer")
        self.sCase = f"{sModel}{self.sDate}{sCase_index}"

        # Set output workspace
        if sWorkspace_output_in is not None:
            self.sWorkspace_output = sWorkspace_output_in
        elif "sWorkspace_output" in aConfig_in:
            self.sWorkspace_output = aConfig_in["sWorkspace_output"]

        # Create output directory
        if self.sWorkspace_output:
            sPath = str(Path(self.sWorkspace_output) / self.sCase)
            self.sWorkspace_output = sPath
            os.makedirs(sPath, exist_ok=True)

    def pyearthbuffer_export(self) -> None:
        """Export the buffer operation results."""
        print("pyearthbuffer started export results")
        ptimer = pytimer()
        ptimer.start()
        # Export logic can be hooked here by subclasses or workflows
        ptimer.stop()

    def tojson(self) -> str:
        """Convert the case object to a JSON string.

        Returns:
            str: A formatted JSON string representing the case object.
        """
        obj = self.__dict__.copy()
        return json.dumps(
            obj,
            sort_keys=True,
            indent=4,
            ensure_ascii=True,
            cls=CaseClassEncoder,
        )

    def pyearthbuffer_print(self) -> None:
        """Print the case object in JSON format."""
        print(self.tojson())
