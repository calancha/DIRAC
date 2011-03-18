# $HeadURL$
__RCSID__ = "$Id$"

from DIRAC import S_OK, S_ERROR
from DIRAC.ConfigurationSystem.Client.Helpers import getCSExtensions

def getCurrentVersion():
  """ Get a string corresponding to the current version of the DIRAC package and all the installed
      extension packages
  """
  import DIRAC
  version = 'DIRAC ' + DIRAC.version

  for ext in getCSExtensions():
    try:
      import imp
      module = imp.find_module( "%sDIRAC" % ext )
      extModule = imp.load_module( "%sDIRAC" % ext, *module )
      version = extModule.version
    except ImportError:
      pass
    except AttributeError:
      pass

  return S_OK( version )

def getVersion():
  """ Get a dictionary corresponding to the current version of the DIRAC package and all the installed
      extension packages
  """

  import DIRAC
  vDict = {'Extensions':{}}
  vDict['DIRAC'] = DIRAC.version

  for ext in getCSExtensions():
    try:
      import imp
      module = imp.find_module( "%sDIRAC" % ext )
      extModule = imp.load_module( "%sDIRAC" % ext, *module )
      vDict['Extensions'][ext] = extModule.version
    except ImportError:
      pass
    except AttributeError:
      pass

  return S_OK( vDict )
