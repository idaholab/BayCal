# Copyright 2022 Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED
#
#
#
"""
Created on July 30 2020
@author: Congjian Wang
"""

from .NormalModel import NormalModel

"""
 Interface Dictionary (factory) (private)
"""
__base = 'LikelihoodBase'
__interfaceDict = {}
__interfaceDict['normal'] = NormalModel

def knownTypes():
  """
    Returns a list of strings that define the types of instantiable objects for
    this base factory.

    returns:
      list: the known types
  """
  return __interfaceDict.keys()

def returnInstance(classType):
  """
    Attempts to create and return an instance of a particular type of object
    available to this factory.

    :param classType: string, string should be one of the knownTypes.

    return:
      instance: subclass object constructed with no arguments
  """
  return returnClass(classType)()

def returnClass(classType):
  """
    Attempts to return a particular class type available to this factory.

    :param classType: string, string should be one of the knownTypes.
    :returns:
      returnClass: class, reference to the subclass
  """
  try:
    return __interfaceDict[classType.lower()]
  except KeyError:
    raise IOError(__name__ + ': unknown ' + __base + ' type ' + classType)
