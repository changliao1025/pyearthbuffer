import os
from pathlib import Path
import json
from json import JSONEncoder
import datetime
import numpy as np

# Import from pyearth instead of local classes
from pyearth.toolbox.date.timer import pytimer

class CaseClassEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, list):
            pass
        return JSONEncoder.default(self, obj)


class pycase(object):
    """
    The pyearthbuffer case class for managing buffer operations.

    Args:
        aConfig_in (dict): A dictionary of configuration parameters
        sDate_in (str, optional): The case date. Defaults to None.
        sWorkspace_output_in (str, optional): The output workspace. Defaults to None.
    """

    iCase_index = 0
    sCase = ''
    sDate = ''
    sWorkspace_output = ''

    def __init__(self, aConfig_in, sDate_in=None, sWorkspace_output_in=None):
        """
        Initialize a pyearthbuffer case object.

        Args:
            aConfig_in (dict): A dictionary of parameters
            sDate_in (str, optional): The case date. Defaults to None.
            sWorkspace_output_in (str, optional): The output workspace. Defaults to None.
        """

        # Set case index
        if 'iCase_index' in aConfig_in:
            iCase_index = int(aConfig_in['iCase_index'])
        else:
            iCase_index = 1

        sCase_index = "{:03d}".format(iCase_index)
        self.iCase_index = iCase_index

        # Set date
        pDate = datetime.datetime.today()
        sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)

        if sDate_in is not None:
            self.sDate = sDate_in
        elif 'sDate' in aConfig_in:
            self.sDate = aConfig_in['sDate']
        else:
            self.sDate = sDate_default

        # Set case name
        if 'sModel' in aConfig_in:
            sModel = aConfig_in['sModel']
        else:
            sModel = 'pyearthbuffer'

        sCase = sModel + self.sDate + sCase_index
        self.sCase = sCase

        # Set output workspace
        if sWorkspace_output_in is not None:
            self.sWorkspace_output = sWorkspace_output_in
        elif 'sWorkspace_output' in aConfig_in:
            self.sWorkspace_output = aConfig_in['sWorkspace_output']

        # Create output directory
        if self.sWorkspace_output:
            sPath = str(Path(self.sWorkspace_output) / sCase)
            self.sWorkspace_output = sPath
            Path(sPath).mkdir(parents=True, exist_ok=True)

    def pyearthbuffer_export(self):
        """
        Export the buffer operation results.
        """
        print('pyearthbuffer started export results')
        ptimer = pytimer()
        ptimer.start()
        # Export logic here
        ptimer.stop()
        return

    def tojson(self):
        """
        Convert the case object to a JSON string.

        Returns:
            str: A JSON string representing the case object
        """
        obj = self.__dict__.copy()
        sJson = json.dumps(obj,
                          sort_keys=True,
                          indent=4,
                          ensure_ascii=True,
                          cls=CaseClassEncoder)
        return sJson

    def pyearthbuffer_print(self):
        """
        Print the case object.
        """
        print(self.tojson())
        return
