########################################################################################################################
#
#TOPOLOGY :
# 				                 ____________       
#  				                |            |   
# 				                |            |     
#                               |            |
#  		[ixia]------------------| Heavenly-2 |------------------[ixia]    
#                               |  		     |
#  				                |            |     
# 				                |____________|     

# 
#Steps which is followed For this Bug CSCwe46569:-
# Step 1:- Configured to the Switch(Heavenly-2)
# Step 2:- Create the monitor s
# Step 3:- Create source vlans.
########################################################################################################################
from ats import tcl
from ats import aetest
from ats.log.utils import banner
import time
import logging
import os
import sys
import re
import pdb
import json
import pprint
import socket
import struct
import inspect
#import nxos.lib.nxos.util as util
#import ctsPortRoutines
#import pexpect
#import nxos.lib.common.topo as topo

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
global uut1           
global uut1_intf1, uut1_intf2



class ForkedPdb(pdb.Pdb):
    '''A Pdb subclass that may be used
    from a forked multiprocessing child1
    '''
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin



################################################################################
####                       COMMON SETUP SECTION                             ####
################################################################################
class common_setup(aetest.CommonSetup):
    @aetest.subsection
    def qos_topo_parse(self,testscript,testbed,R1):
        global uut1
        global uut1_intf1, uut1_intf2

        global uut_m

        global custom
        custom = testbed.custom

        uut1=testbed.devices[R1]
        uut1_intf1=uut1.interfaces['uut1_ixia_1'].intf
        uut1_intf1=uut1.interfaces['uut1_ixia_2'].intf

        uut_list=[uut1]

        router_list = [R1]

    @aetest.subsection
    def connect_to_devices(self,testscript,testbed,R1):
        global uut1

         
        log.info("Connecting to Device:%s"%uut1.name)
        try:
            uut1.connect()
            log.info("Connection to %s Successful..."%uut1.name)
        except Exception as e:
            log.info("Connection to %s Unsuccessful "\
                      "Exiting error:%s"%(uut1.name,e))
            self.failed(goto=['exit'])


################################################################################
###                          TESTCASE BLOCK                                  ###
################################################################################

###############################################################################################
# Test case 1 :
###############################################################################################

class Sys_log_collection(aetest.Testcase):

    "Verifying show Tech-support aclqos"

    @aetest.test
    def tc01_test(self):
        ##################################################################

        log.info("Collecting internal build version")
        cmd = "sh version internal build-identifier"
        output = uut1.execute(cmd)
        
        log.info("Check The Feature Vlan")
        cmd = """sh feature 
              """
        output = uut1.configure(cmd)
        match = re.search("private-vlan           1          enabled ",output)
        if match :
            log.info("testcase is passed")
        else :	
            log.info("fail")
            
        log.info("Configure Vlan 50")
        cmd = """vlan 50
                 private-vlan primary
                 vlan 60
                 private-vlan isolated 
                 vlan 62
                 private-vlan community
                 exit
              """
        output = uut1.configure(cmd)
        
        log.info("Configure Vlan 50")
        cmd = """vlan 50
                 private-vlan association 60,62 
              """
        output = uut1.configure(cmd)
        
        log.info("Configure Interface Eth1/37")
        cmd = """default interface eth1/37
                 interface eth1/37
                 switchport
                 switchport mode private-vlan trunk promiscuous
                 switchport private-vlan mapping trunk 50 60,62
                 no shut
               """
        output = uut1.configure(cmd)
        log.info("Configure Interface Eth1/38")
        cmd = """default interface eth1/38
                 interface eth1/38
                 switchport
                 switchport mode private-vlan trunk secondary
                 switchport private-vlan mapping trunk 50 60
                 no shut
              """
        output = uut1.configure(cmd)
            
        log.info("Check The Feature Vlan")
        cmd = """show consistency-checker membership vlan 50 private-vlan brief 
              """
        output = uut1.configure(cmd)
        match = re.search("PASSED",output)
        if match :
            log.info("testcase is passed")
        else :
            log.info("fail")
            
        
################################################################################
####                       COMMON CLEANUP SECTION                           ####
################################################################################

if __name__ == '__main__': # pragma: no cover
    import argparse
    from ats import topology
    parser = argparse.ArgumentParser(description='standalone parser')
    parser.add_argument('--testbed', dest='testbed', type=topology.loader.load)
    parser.add_argument('--R1', dest='R1', type=str)
    parser.add_argument('--mode',dest = 'mode',type = str)
    args = parser.parse_known_args()[0]
    aetest.main(testbed=args.testbed,
                R1_name=args.R1,
                mode = args.mode,
                pdb = True)
