########################################################################
# $HeadURL $
# File: RegistrationTask.py
# Author: Krzysztof.Ciba@NOSPAMgmail.com
# Date: 2011/10/20 12:06:50
########################################################################

""" :mod: RegistrationTask 
    =======================
 
    .. module: RegistrationTask
    :synopsis: 
    .. moduleauthor:: Krzysztof.Ciba@NOSPAMgmail.com
    
"""

__RCSID__ = "$Id $"

##
# @file RegistrationTask.py
# @author Krzysztof.Ciba@NOSPAMgmail.com
# @date 2011/10/20 12:06:59
# @brief Definition of RegistrationTask class.

## imports 
from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.private.RequestTask import RequestTask

########################################################################
class RegistrationTask( RequestTask ):
  """
  .. class:: RegistrationTask
  
  """

  def __init__( self, *args, **kwargs ):
    """c'tor

    :param self: self reference
    """
    RequestTask.__init__( self, *args, **kwargs )
    self.setRequestType( "register" )
    self.addOperationAction( "registerFile", self.registerFile )

  def registerFile( self, index, requestObj, subRequestAttrs, subRequestFiles ):
    """ registerFile operation handler

    :param self: self reference
    :param int index: execution order index
    :param RequestContainer requestObj: a request object
    :param subRequestAttrs: SubRequest attributes
    :param subRequestFiles: subRequest files
    """
    self.always( "Processing subrequest %d registerFile" % index )

    ## list of targetSE
    targetSEs = list( set( [ targetSE.strip() for targetSE in  subRequestAttrs["TargetSE"].split(",") ] ) )
    if not targetSEs:
      targetSEs = [ "CERN-FAILOVER" ]
    ## dict for failed LFNs
    failed = {}
    ## subrequest error if any
    subRequestError = ""

    catalogue = subRequestAttrs["Catalogue"]
    if not catalogue:
      catalogue = ""
    elif catalogue == "BookkeepingDB":
      catalogue = "CERN-HIST"

    for subRequestFile in subRequestFiles:
      lfn = subRequestFile.get( "LFN", "" ) 
      failed.setdefault( lfn, {} )
      self.info("Processing file %s" % lfn )
      if subRequestFile["Status"] != "Waiting":
        self.info("Skipping file %s, status is %s" % ( lfn, subRequestFile["Status"] ) )
        continue
      pfn = subRequestFile.get( "PFN", "" ) 
      size = subRequestFile.get( "Size", 0 ) 
      guid = subRequestFile.get( "GUID", "" ) 
      addler = subRequestFile.get( "Addler", "" ) 

      for targetSE in targetSEs:
        fileTuple = ( lfn, pfn, size, targetSE, guid, addler )
        res = self.replicaManager().registerFile( fileTuple, catalogue )
        
        if not res["OK"] or lfn in res["Value"]["Failed"]:
          self.dataLoggingClient().addFileRecord( lfn, "RegisterFail", targetSE, "", "RegistrationTask" )
          reason = res["Message"] if not res["OK"] else "registration in ReplicaManager failed"
          errorStr = "Failed to register LFN %s: %s" % ( lfn, reason )
          failed[lfn][targetSE] = reason
          subRequestError = reason
          self.error( errorStr )
        else:
          self.dataLoggingClient().addFileRecord( lfn, "Register", targetSE, "", "RegistrationTask" )
          self.info( "File %s has been registered at %s." % ( lfn, targetSE ) )
     
      if not failed[lfn]:
        requestObj.setSubRequestFileAttributeValue( index, "register", lfn, "Status", "Done")
        self.info( "File %s has been registered at all targetSEs" % lfn )

    ##################################################################
    ## all files were registered or no files at all in this subrequest
    if not subRequestError:
      requestObj.setSubRequestStatus( index, "register", "Done" )
      self.debug( "Subrequest %d status has been set to 'Done'." % index )
    else:
      subRequestError = "Registration failed for LFNs: %s" % ", ".join( failed.keys() )  
      return S_ERROR( subRequestError )
    ## return requestObj
    return S_OK( requestObj )
          
    
