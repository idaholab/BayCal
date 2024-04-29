# Copyright 2022 Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED
"""
  Author:  Congjian Wang
  Date  :  07/16/2020
"""

#External Modules---------------------------------------------------------------
import numpy as np
import math
import logging
#External Modules End-----------------------------------------------------------

#Internal Modules---------------------------------------------------------------
from . import LikelihoodModels
from ravenframework.utils import mathUtils as utils
from ravenframework.utils import InputData
from ravenframework.utils import InputTypes
from ravenframework.PluginBaseClasses.ExternalModelPluginBase import ExternalModelPluginBase
#Internal Modules End-----------------------------------------------------------

## option to use logging
# logging.basicConfig(format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
# logger = logging.getLogger()
# fh = logging.FileHandler(filename='logos.log', mode='w')
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
# fh.setFormatter(formatter)
# logger.addHandler(fh)

class LikelihoodModel(ExternalModelPluginBase):
  """
    RAVEN ExternalModel of Likelihood Function that can be combine with
    MCMC Sampler for Bayesian calibration
  """

  def __init__(self):
    """
      Constructor

      :returns: None
      """
    ExternalModelPluginBase.__init__(self)
    self.type = self.__class__.__name__
    self.name = self.__class__.__name__
    self._model = None
    self._modelType = None
    self._modelXMLInput = None

  def _readMoreXML(self, container, xmlNode):
    """
      Method to read the portion of the XML that belongs to this plugin

      :param container: object, self-like object where all the variables can be stored
      :param xmlNode: xml.etree.ElementTree.Element, XML node that needs to be read

      :returns: None
    """
    variables = xmlNode.find('variables')
    inputVars = xmlNode.find('inputs')
    outputVars = xmlNode.find('outputs')
    if variables is not None and (inputVars is not None or outputVars is not None):
      raise IOError("Botht 'variables' node and 'inputs/outputs' are provided! This is not allowed, please consider just use one of them.")
    if variables is not None:
      delimiter = ',' if ',' in variables.text else None
      container.variables = [var.strip() for var in variables.text.split(delimiter)]
    elif inputVars is not None and outputVars is not None:
      delimiter = ',' if ',' in inputVars.text else None
      container.variables = [var.strip() for var in inputVars.text.split(delimiter)]
      delimiter = ',' if ',' in outputVars.text else None
      container.variables.extend([var.strip() for var in outputVars.text.split(delimiter)])
    self._modelXMLInput = xmlNode.find('LikelihoodModel')
    self._modelType = self._modelXMLInput.get('type')
    if self._modelType is None:
      raise IOError("Required attribute 'type' for node '{}' is not provided!".format(self.name))
    self._model = LikelihoodModels.returnInstance(self._modelType)

  def initialize(self, container,runInfoDict,inputFiles):
    """
      Method to initialize this plugin

      :param container: object, self-like object where all the variables can be stored
      :param runInfoDict: dict, dictionary containing all the RunInfo parameters (XML node <RunInfo>)
      :param inputFiles: list, list of input files (if any)

      :returns: None
    """
    pass

  def run(self, container, inputDict):
    """
      This is a simple example of the run method in a plugin.

      :param container: object, self-like object where all the variables can be stored
      :param inputDict: dict, dictionary of inputs from RAVEN

      :returns: None
    """
    self._model.handleInput(self._modelXMLInput)
    self._model.initialize(inputDict)
    self._model.run()
    outputDict = self._model.getOutputs()
    for key, val in outputDict.items():
      setattr(container, key, val)
