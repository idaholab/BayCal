# Copyright 2022 Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED
"""
Created on July 30 2020
@author: Congjian Wang
"""

#External Modules------------------------------------------------------------------------------------
import numpy as np
#External Modules End--------------------------------------------------------------------------------

#Internal Modules------------------------------------------------------------------------------------
from ravenframework.utils import mathUtils as utils
from ravenframework.utils import InputData, InputTypes
from .LikelihoodBase import LikelihoodBase
#Internal Modules End--------------------------------------------------------------------------------

class NormalModel(LikelihoodBase):
  """
    Normal/Multivariate Normal Likelihood model
  """

  @classmethod
  def getInputSpecification(cls):
    """
      Collects input specifications for this class.

      returns:
        InputData: RAVEN InputData specs
    """
    inputSpecs = super(NormalModel, cls).getInputSpecification()
    inputSpecs.description = r"""
      Normal/Multivariate Normal Likelihood model
      """
    inputSpecs.addSub(InputData.parameterInputFactory('simTargets', contentType=InputTypes.InterpretedListType,
      descr='Targets of simulations that are used in calibration'))
    expTargetsInp = InputData.parameterInputFactory('expTargets', contentType=InputTypes.InterpretedListType,
      descr='Targets of experiments that are used in calibration')
    expTargetsInp.addParam('shape', InputTypes.IntegerListType, required=False,
      descr=r"""determine the number of targets and the number of experimental observations for each
      targets. For example, \xmlAttr{shape}=``3,2'' will indicate 2 targets and 3 observations for each
      targets. While \xmlAttr{shape}=``10'' will indicate one target with 10 observations. Omitting this
      optional attribute will result a single target with multiple observations instead.""" )
    expTargetsInp.addParam('computeCov', InputTypes.BoolType, required=False,
      descr=r"""Indicate whether the experiment covariance matrix is provided or computed based on given experiment
      observations. If True, we will compute the covariance based on given observations, else, the user need to
      provide the covariance matrix.""")
    expTargetsInp.addParam('correlation', InputTypes.BoolType, required=False,
      descr=r"""Indicate whether the targets are correlated or not. If True, and ``compute'' is True, we will
      compute the covariance matrix, elif False and ``compute'' is True, we will only compute the variance of
      each target.""")
    inputSpecs.addSub(expTargetsInp)
    inputSpecs.addSub(InputData.parameterInputFactory('biasTargets', contentType=InputTypes.InterpretedListType,
      descr='Model uncertainty/discrepancy/bias/error in Targets that are used in calibration'))
    expCovInp = InputData.parameterInputFactory('expCov', contentType=InputTypes.InterpretedListType,
      descr='Experiment covariance, i.e. measurement noise')
    expCovInp.addParam('diag', InputTypes.BoolType, required=False,
      descr=r"""If True, only variance for each target is required to provide, else, the user need to provide
      the full covariance matrix.""")
    inputSpecs.addSub(expCovInp)
    biasCovInp = InputData.parameterInputFactory('biasCov', contentType=InputTypes.InterpretedListType,
      descr='Model covariance, model bias/discrepancy or model inadequacy caused by missing physics or numerical approximation')
    biasCovInp.addParam('diag', InputTypes.BoolType, required=False,
      descr=r"""If True, only variance for each target is required to provide, else, the user need to provide
      the full covariance matrix.""")
    inputSpecs.addSub(biasCovInp)
    romCovInp = InputData.parameterInputFactory('romCov', contentType=InputTypes.InterpretedListType,
      descr='Metamodel covariance, i.e. model uncertainty caused by surrogate model, such as interpolation')
    romCovInp.addParam('diag', InputTypes.BoolType, required=False,
      descr=r"""If True, only variance for each target is required to provide, else, the user need to provide
      the full covariance matrix.""")
    inputSpecs.addSub(romCovInp)
    reductionInp = InputData.parameterInputFactory('reduction',
      descr=r"""Allows reduction on likelihood model construction""")
    reductionInp.addSub(InputData.parameterInputFactory('type', contentType=InputTypes.StringType,
      descr='The method used for reduction, default is "PCA"'))
    reductionInp.addSub(InputData.parameterInputFactory('truncationRank', contentType=InputTypes.FloatType,
      descr='the truncation rank'))
    basisInp = InputData.parameterInputFactory('basis', contentType=InputTypes.FloatListType,
      descr=r"""user provided basis vector for reduction""")
    basisInp.addParam('shape', InputTypes.IntegerTupleType, required=True,
      descr=r"""determine the basis vectors for reduction.
      For example, \xmlAttr{shape}=``10,2'' will indicate 2 basis vectors with dimension 10""" )
    reductionInp.addSub(basisInp)

    inputSpecs.addSub(reductionInp)

    return inputSpecs

  def __init__(self):
    """
      Constructor

      :return: None
    """
    LikelihoodBase.__init__(self)
    self._simTargets = None
    self._expTargets = None
    self._biasTargets = np.array([0])
    self._expTargetsShape = None
    self._expCov = None
    self._computeExpCov = True # Default to compute the expCov from provided data
    self._correlatedExpCov = False # Assume the experimental data are uncorrelated unless the attribute "correlation" is set to True
    self._biasCov = None
    self._romCov = None
    self._cov = None
    self._detCov = None
    self._diag = {}
    self._multipleTargets = False
    self._numObservations = None
    self._reductionType = 'pca'
    self._truncationRank = None
    self._subspace = None

  def _localHandleInput(self, paramInput):
    """
      Function to read the portion of the parsed xml input that belongs to this specialized class
      and initialize some stuff based on the inputs got.

      :param paramInput: InputData.ParameterInput, the parsed xml input

      :returns: None
    """
    LikelihoodBase._localHandleInput(self, paramInput)
    for child in paramInput.subparts:
      if child.getName().lower() == 'simtargets':
        self._simTargets = self.setVariable(child.value)
        self._variableDict['_simTargets'] = self._simTargets
      elif child.getName().lower() == 'exptargets':
        self._expTargets = self.setVariable(child.value)
        self._variableDict['_expTargets'] = self._expTargets
        self._expTargetsShape = child.parameterValues.get('shape', None)
        self._computeExpCov = child.parameterValues.get('computeCov', True)
        self._correlatedExpCov = child.parameterValues.get('correlation', False)
      elif child.getName().lower() == 'biastargets':
        self._biasTargets = self.setVariable(child.value)
        self._variableDict['_biasTargets'] = self._biasTargets
      elif child.getName().lower() == 'expcov':
        self._expCov = self.setVariable(child.value)
        self._variableDict['_expCov'] = self._expCov
        diag = child.parameterValues.get('diag', False)
        self._diag['_expCov'] = diag
      elif child.getName().lower() == 'biasCov':
        self._biasCov = self.setVariable(child.value)
        self._variableDict['_biasCov'] = self._biasCov
        diag = child.parameterValues.get('diag', False)
        self._diag['_biasCov'] = diag
      elif child.getName().lower() == 'romcov':
        self._romCov = self.setVariable(child.value)
        self._variableDict['_romCov'] = self._romCov
        diag = child.parameterValues.get('diag', False)
        self._diag['_romCov'] = diag
      elif child.getName() == 'reduction':
        typeNode = child.findFirst('type')
        if typeNode:
          self._reductionType = typeNode.value.lower()
        truncationRankNode = child.findFirst('truncationRank')
        if truncationRankNode:
          self._truncationRank = truncationRankNode.value
        basisNode = child.findFirst('basis')
        if basisNode:
          shape = basisNode.parameterValues.get('shape', None)
          if shape:
            self._subspace = np.reshape(basisNode.value, shape)
          else:
            raise IOError('shape attribute is required for node "basis"')
    if self._simTargets is None:
      raise IOError('simTargets is required but it can not be found in the input XML file!')
    if self._expTargets is None:
      raise IOError('expTargets is required but it can not be found in the input XML file!')
    if not self._computeExpCov and self._expCov is None:
      raise IOError('expCov is required but it can not be found in the input XML file!')
    if self._reductionType != 'pca':
      raise IOError('Reduction type "{}" is not valid, please use "pca"!'.format(self._reductionType))

  def _checkInputParams(self, needDict):
    """
      Method to check input parameters

      :param needDict: dict, dictionary of required parameters

      :returns: None
    """
    LikelihoodBase._checkInputParams(self, needDict)
    if self._expTargetsShape:
      try:
        self._expTargets = np.reshape(self._expTargets, self._expTargetsShape)
      except ValueError:
        print('The length of provided "expTargets" is not correct!')
        raise IOError('The length of provided "expTargets" is not correct!')
    else:
      self._expTargets = np.reshape(self._expTargets, (-1,1))
    self._numObservations = self._expTargets.shape[0]
    if self._computeExpCov:
      # if self._expCov:
        # print('"WARNING:" The "expCov" will be computed from the provided data "expTargets", the user provided "expCov" will not be used.' \
        #   + 'Try to disable "computeCov" attribute of "expTargets" to use the provided "expCov"!')
      self._expCov = np.cov(self._expTargets.T)
      if self._expCov.size == 1:
        self._expCov = self._expCov.reshape(1,1)
      if self._correlatedExpCov:
        self._expCov = np.ravel(self._expCov)
        self._diag['_expCov'] = False
      else:
        self._expCov = np.diag(self._expCov)
        self._diag['_expCov'] = True
    dim = len(self._simTargets)
    if dim != self._expTargets.shape[-1]:
      raise IOError('"simTargets" should have the same size as "expTargets", but get "{}" != "{}"'.format(dim, len(self._expTargets)))
    if len(self._biasTargets) != 1:
      if dim != len(self._biasTargets):
        raise IOError('"simTargets" should have the same size as "biasTargets", but get "{}" != "{}"'.format(dim, len(self._biasTargets)))
    self._cov = None
    for var, val in self._diag.items():
      if not (var == '_expCov' and self._computeExpCov):
        dimCov = len(getattr(self, var))
        if val:
          if dim != dimCov:
            raise IOError('"{}" should have the same size as "simTargets", but get "{}" != "{}"'.format(var, dimCov, dim))
          else:
            setattr(self, var, np.diag(getattr(self, var)))
        else:
          if dimCov != dim * dim:
            raise IOError('The size of "{}" should be the square of the size of "simTargets", but get "{}" != "{}" * "{}"'.format(var, dimCov, dim, dim))
          else:
            setattr(self, var, getattr(self, var).reshape(dim, dim))
      if self._cov is None:
        self._cov = getattr(self, var)
      else:
        self._cov += getattr(self, var)
    if not np.allclose(self._cov, self._cov.T):
      raise IOError('Provided covariance matrix is not symmetric!')
    if self._cov.size > 1:
      self._multipleTargets = True
      if not self.isPosDef(self._cov):
        raise IOError('Provided covariance matrix is not postive definite!')
      if self._subspace is None and self._truncationRank:
        self._subspace, _, _ = utils.computeTruncatedSingularValueDecomposition(self._cov, self._truncationRank)
        # update covariance with reduction, size reduced from N by N to r by r, i.e. Ur.T * Cov * Ur
        self._cov = np.dot(self._subspace.T, np.matmul(self._cov, self._subspace))
      elif self._subspace is not None:
        # update covariance with reduction, size reduced from N by N to r by r, i.e. Ur.T * Cov * Ur
        self._cov = np.dot(self._subspace.T, np.matmul(self._cov, self._subspace))
      self._detCov = np.sqrt(np.linalg.det(self._cov))
    else:
      self._detCov = np.sqrt(self._cov)

  @staticmethod
  def isPosDef(arrayIn):
    """
      Check if provided array is postive definite or not.

      :param arrayIn: numpy.array, input array

      returns:
        bool: True if the array is postive definite
    """
    try:
      np.linalg.cholesky(arrayIn)
      return True
    except np.linalg.LinAlgError:
      return False

  def initialize(self, inputDict):
    """
      Method to initialize this plugin

      :param inputDict: dict, dictionary of inputs
      :returns: None
    """
    LikelihoodBase.initialize(self, inputDict)

  def _logLikelihoodFunction(self):
    """
      Function to calculate log probability

      returns:
        dict: likelihood output
    """
    output = {}
    invCov = None
    tot = 0.
    if not self._multipleTargets:
      invCov = 1./self._cov
      delta = self._expTargets- self._simTargets - self._biasTargets
      delta = np.ravel(delta)
      tot += 0.5 * np.dot(delta, delta) * invCov
      tot *= -1.0
    else:
      invCov = np.linalg.inv(self._cov)
      if self._subspace is None:
        for i in range(self._expTargets.shape[0]):
          delta = self._expTargets[i] - self._simTargets - self._biasTargets
          delta = np.ravel(delta)
          tot += 0.5 * np.dot(delta, np.matmul(invCov, delta))
        tot *= -1.0
      else:
        for i in range(self._expTargets.shape[0]):
          delta = self._expTargets[i] - self._simTargets - self._biasTargets
          # apply subspace
          delta = np.dot(self._subspace.T, np.ravel(delta))
          tot += 0.5 * np.dot(delta, np.matmul(invCov, delta))
        tot *= -1.0
    # include the 1/sqrt(det(cov)) for all observations
    tot -= self._numObservations * np.log(self._detCov)
    # netLogLikelihood
    output['likelihood'] = np.atleast_1d(tot)
    return output
