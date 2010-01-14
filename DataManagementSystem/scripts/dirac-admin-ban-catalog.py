#!/usr/bin/env python
########################################################################
# $HeadURL: svn+ssh://svn.cern.ch/reps/dirac/DIRAC/trunk/DIRAC/DataManagementSystem/scripts/dirac-admin-ban-catalog.py $
########################################################################
__RCSID__   = "$Id: dirac-admin-ban-catalog.py 18161 2009-11-11 12:07:09Z acsmith $"
__VERSION__ = "$Revision: 1.3 $"
import DIRAC
from DIRAC.Core.Base                                   import Script

Script.parseCommandLine(ignoreErrors = True)

sites = Script.getPositionalArgs()

def usage():
  gLogger.info('dirac-admin-ban-catalog Tier1 [Tier1 ...]')
  gLogger.info(' Type "%s --help" for the available options and syntax' % Script.scriptName)
  DIRAC.exit(-1)

from DIRAC.ConfigurationSystem.Client.CSAPI           import CSAPI
from DIRAC.FrameworkSystem.Client.NotificationClient  import NotificationClient
from DIRAC.Core.Security.Misc                         import getProxyInfo
from DIRAC                                            import gConfig,gLogger
csAPI = CSAPI()

res = getProxyInfo()
if not res['OK']:
  gLogger.error("Failed to get proxy information",res['Message'])
  DIRAC.exit(2)
userName = res['Value']['username']
group = res['Value']['group']
if group != 'diracAdmin':
  gLogger.error("You must be diracAdmin to execute this script")
  gLogger.info("Please issue 'lhcb-proxy-init -g diracAdmin'")
  DIRAC.exit(2)

if not sites:
  usage()

catalogCFGBase = "/Resources/FileCatalogs/LcgFileCatalogCombined"
banned = []
for site in sites:
  res = gConfig.getOptionsDict('%s/%s' % (catalogCFGBase,site))
  if not res['OK']:
    gLogger.error("The provided site (%s) does not have an associated catalog." % site)
    continue
  
  res = csAPI.setOption("%s/%s/Status" % (storageCFGBase,site),"InActive")
  if not res['OK']:
    gLogger.error("Failed to update %s catalog status to InActive" % site)
  else:
    gLogger.debug("Successfully updated %s catalog status to InActive" % site)
    banned.append(site)

if not banned:
  gLogger.error("Failed to ban any catalog mirrors")
  DIRAC.exit(-1)

res = csAPI.commitChanges()
if not res['OK']:
  gLogger.error("Failed to commit changes to CS",res['Message'])
  DIRAC.exit(-1)

subject = '%d catalog instance(s) banned for use' % len(banned)
address = gConfig.getValue('/Operations/EMail/Production','lhcb-grid@cern.ch')
body = 'The catalog mirrors at the following sites were banned'
for site in banned:
  body = "%s\n%s" % (body,site)
NotificationClient().sendMail(address,subject,body,'%s@cern.ch' % userName)
DIRAC.exit(0)
