import unittest
import mock
import os
import json
from tempfile import NamedTemporaryFile

from mocks import send_request

from pynxos.device import Device, RebootSignal, CLIError

CURRNENT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestDevice(unittest.TestCase):

    @mock.patch('pynxos.device', autospec=True)
    @mock.patch('pynxos.device.RPCClient')
    def setUp(self, mock_rpc, mock_node):
        self.device = Device('host', 'user', 'pass')
        self.rpc = mock_rpc
        self.send_request = mock_rpc.return_value.send_request
        self.send_request.side_effect = send_request


    def test_init(self):
        self.assertEqual(self.device.host, 'host')
        self.assertEqual(self.device.username, 'user')
        self.assertEqual(self.device.password, 'pass')
        self.assertEqual(self.device.transport, 'http')
        self.assertEqual(self.device.timeout, 30)

        self.rpc.assert_called_with('host', 'user', 'pass', transport='http', port=None)

    def test_show(self):
        result = self.device.show('sh clock')
        expected = {'simple_time': '18:06:31.021 UTC Tue Mar 22 2016\n'}

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['sh clock'], method=u'cli', timeout=30)

    def test_show_empty_response(self):
        self.send_request.return_value = []
        self.send_request.side_effect = None

        result = self.device.show('sh clock')
        expected = {}

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['sh clock'], method=u'cli', timeout=30)

    def test_show_raw_text(self):
        result = self.device.show('sh clock', raw_text=True)
        expected = '18:29:19.583 UTC Tue Mar 22 2016\n'

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['sh clock'], method=u'cli_ascii', timeout=30)

    def test_show_list(self):
        result = self.device.show_list(['sh clock', 'sh hostname'])
        expected = [{'simple_time': '18:52:45.084 UTC Tue Mar 22 2016\n'}, {'hostname': 'N9K2.ntc.com'}]

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['sh clock', 'sh hostname'], method=u'cli', timeout=30)

    def test_show_list_raw_text(self):
        result = self.device.show_list(['sh clock', 'sh hostname'], raw_text=True)
        expected = ['18:55:38.720 UTC Tue Mar 22 2016\n', 'N9K2.ntc.com \n']

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['sh clock', 'sh hostname'], method=u'cli_ascii', timeout=30)

    def test_config(self):
        result = self.device.config('int ethernet 1/1')
        expected = None

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['int ethernet 1/1'], method=u'cli', timeout=30)

    def test_config_list(self):
        result = self.device.config_list(['int ethernet 1/1', 'no shutdown'])
        expected = [None, None]

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['int ethernet 1/1', 'no shutdown'], method=u'cli', timeout=30)

    def test_save(self):
        result = self.device.save()
        expected = True

        self.assertEqual(result, expected)
        self.send_request.assert_called_with([u'copy run startup-config'], method=u'cli_ascii', timeout=30)

    def test_save_error(self):
        result = self.device.save(filename='abc')
        expected = False

        self.assertEqual(result, expected)
        self.send_request.assert_called_with([u'copy run abc'], method=u'cli_ascii', timeout=30)

    @mock.patch('pynxos.device.FileCopy')
    def test_file_copy_remote_exists(self, mock_fc):
        mock_fc.return_value.remote_file_exists.return_value = True
        result = self.device.file_copy_remote_exists('source', dest='dest')

        self.assertEqual(result, True)
        mock_fc.assert_called_with(self.device, 'source', dst='dest', file_system='bootflash:')

    @mock.patch('pynxos.device.FileCopy')
    def test_file_copy_remote_doesnt_exist(self, mock_fc):
        mock_fc.return_value.remote_file_exists.return_value = False
        result = self.device.file_copy_remote_exists('source', dest='dest')

        self.assertEqual(result, False)
        mock_fc.assert_called_with(self.device, 'source', dst='dest', file_system='bootflash:')

    @mock.patch('pynxos.device.FileCopy')
    def test_file_copy(self, mock_fc):
        result = self.device.file_copy('source', dest='dest')

        mock_fc.assert_called_with(self.device, 'source', dst='dest', file_system='bootflash:')
        mock_fc.return_value.send.assert_called_with()

    @mock.patch.object(Device, 'show')
    def test_reboot(self, mock_show):
        self.device.reboot(confirm=True)

        mock_show.assert_any_call('terminal dont-ask')
        mock_show.assert_any_call('reload')

    @mock.patch.object(Device, 'show')
    def test_set_boot_options(self, mock_show):
        self.device.set_boot_options('boot.sys')
        mock_show.assert_called_with('install all nxos boot.sys', raw_text=True)

    @mock.patch.object(Device, 'show')
    def test_set_boot_options_kickstart(self, mock_show):
        self.device.set_boot_options('boot.sys', kickstart='boot.kick')
        mock_show.assert_called_with('install all system boot.sys kickstart boot.kick', raw_text=True)

    def test_get_boot_options(self):
        result = self.device.get_boot_options()
        expected = {'sys': 'nxos.7.0.3.I2.1.bin', 'status': 'This is the log of last installation.\nVerifying image bootflash:/nxos.7.0.3.I2.1.bin for boot variable "nxos".\n -- SUCCESS\nVerifying image type.\n -- SUCCESS\nPreparing "nxos" version info using image bootflash:/nxos.7.0.3.I2.1.bin.\n -- SUCCESS\nPreparing "bios" version info using image bootflash:/nxos.7.0.3.I2.1.bin.\n -- SUCCESS\nPerforming module support checks.\n -- SUCCESS\nNotifying services about system upgrade.\n -- SUCCESS\nCompatibility check is done:\nModule  bootable          Impact  Install-type  Reason\n------  --------  --------------  ------------  ------\n     1       yes      disruptive         reset  Reset due to single supervisor\nImages will be upgraded according to following table:\nModule       Image                  Running-Version(pri:alt)           New-Version  Upg-Required\n------  ----------  ----------------------------------------  --------------------  ------------\n     1        nxos                               6.1(2)I3(1)           7.0(3)I2(1)           yes\n     1        bios     v07.15(06/29/2014):v07.06(03/02/2014)    v07.34(08/11/2015)           yes\nSwitch will be reloaded for disruptive upgrade.\nInstall is in progress, please wait.\nPerforming runtime checks.\n -- SUCCESS\nSetting boot variables.\n -- SUCCESS\nPerforming configuration copy.\n -- SUCCESS\nModule 1: Refreshing compact flash and upgrading bios/loader/bootrom.\nWarning: please do not remove or power off the module at this time.\n -- SUCCESS\nFinishing the upgrade, switch will reboot in 10 seconds.\n'}

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['show install all status'], method=u'cli_ascii', timeout=30)

    def test_get_boot_options_kickstart(self):
        def special_send_request(commands, method='cli', timeout=30.0):
            if commands == ['show boot']:
                return json.load(open(os.path.join(CURRNENT_DIR, 'mocks', 'send_request_raw', 'show_boot_kick.json')))
            elif commands == ['show install all status']:
                return json.load(open(os.path.join(CURRNENT_DIR, 'mocks', 'send_request_raw', 'show_install_all_status_kick.json')))

        self.send_request.side_effect = special_send_request

        result = self.device.get_boot_options()
        expected = {'sys': 'n5000-uk9.7.2.1.N1.1.bin', 'status': 'This is the log of last installation.\nContinuing with installation process, please wait.\nThe login will be disabled until the installation is completed.\nPerforming supervisor state verification. \nSUCCESS\nSupervisor non-disruptive upgrade successful.\nInstall has been successful.\n', 'kick': 'n5000-uk9-kickstart.7.2.1.N1.1.bin'}

        self.assertEqual(result, expected)
        self.send_request.assert_called_with(['show install all status'], method=u'cli_ascii', timeout=30)

    @mock.patch.object(Device, 'show')
    def test_rollback(self, mock_show):
        self.device.rollback('rb_file')
        mock_show.assert_called_with('rollback running-config file rb_file', raw_text=True)

    @mock.patch.object(Device, 'show_list')
    def test_checkpoint(self, mock_show_list):
        self.device.checkpoint('cp_file')
        mock_show_list.assert_called_with(['terminal dont-ask', 'checkpoint file cp_file'], raw_text=True)

    def test_running_config(self):
        result = self.device.running_config
        expected = '!Command: show running-config\n!Time: Tue Mar 22 21:23:11 2016\nversion 7.0(3)I2(1)\nhostname N9K2\nvdc N9K2 id 1\n  limit-resource vlan minimum 16 maximum 4094\n  limit-resource vrf minimum 2 maximum 4096\n  limit-resource port-channel minimum 0 maximum 511\n  limit-resource u4route-mem minimum 248 maximum 248\n  limit-resource u6route-mem minimum 96 maximum 96\n  limit-resource m4route-mem minimum 58 maximum 58\n  limit-resource m6route-mem minimum 8 maximum 8\nfeature telnet\nfeature nxapi\nfeature bash-shell\nfeature scp-server\nfeature vrrp\nfeature tacacs+\ncfs eth distribute\nfeature pim\nfeature udld\nfeature interface-vlan\nfeature hsrp\nfeature lacp\nfeature dhcp\nfeature vpc\nfeature lldp\nfeature vtp\nonep\n  session key-required enabled\nno password strength-check\nusername admin password 5 $1$6Anve29g$aKsAE8iRKAQzY7sW1qKZh0  role network-admin\nusername cisco password 5 $1$nGd5VWnS$LJ/a9ztNEt6xruMCG2Erl/  role network-admin\nusername jay password 5 $1$K6cIEEfy$vkYaWr5tEdgr55C86b74u/  role network-operator\nusername ntc password 5 $1$0WWXa9uW$EnQSp3nRPD.nIZTqAE//11  role network-admin\nusername netauto password 5 $1$ITxT/Gi0$QbHUtgzTCFt39i4FYSuzl1  role network-admin\nnxapi http port 80\nnxapi https port 443\nbanner motd *\nDISCONNECT FROM DEVICE IMMEDIATELY.\nIF YOU CONTINUE, YOU WILL BE PROSECUTED TO THE FULLEST\nEXTENT OF THE LAW!!!!\n*\nssh login-attempts 10\nip domain-lookup\nip domain-name ntc.com\nip name-server 208.67.222.222\nip host puppet 176.126.88.189\ntacacs-server timeout 10\ntacacs-server deadtime 30\ntacacs-server host 5.6.7.8 \ntacacs-server host 1.2.3.4 key 7 "\\"hello\\"" \nradius-server host 1.2.3.4 authentication accounting \nobject-group ip address OBJECTGROUP-IP\n  10 1.1.1.1/24 \n  20 2.2.2.2/24 \nip access-list INBOUND_MGMT\n  statistics per-entry\n  20 permit tcp 63.118.185.0/24 10.1.100.21/32 eq 22 \n  30 permit icmp any 10.1.100.21/32 \n  40 permit tcp any 10.1.100.21/32 eq 443 \n  50 permit tcp any 10.1.100.21/32 eq www \n  60 permit ip 10.1.100.0/24 10.1.100.21/32 \n  80 permit tcp 89.101.133.0/24 10.1.100.21/32 eq 22 \n  90 permit udp any 10.1.100.21/32 eq snmp \n  100 permit udp any 10.1.100.20/32 eq snmp \n  110 permit tcp 79.52.99.64/32 10.1.100.21/32 eq 22 \n  120 permit tcp 176.126.88.189/32 10.1.100.21/32 eq 22 \nip access-list MYACL\n  10 permit tcp 1.1.1.1/32 eq www any established log \n  20 deny udp 2.1.1.1/20 neq 80 5.5.5.0/24 eq 443 \n  40 remark COMMENT REMARK BY ANSIBLE\n  100 permit ip 10.1.1.1/32 100.1.1.1/24 log \nip access-list ONE\n  15 deny eigrp 1.1.1.1/32 2.2.2.2/32 \n  30 permit tcp any gt smtp any lt 33 urg ack psh rst syn fin established dscp cs7 log \n  40 permit eigrp any any precedence flash fragments time-range RANGE log \n  50 permit udp any range 10 20 any dscp af11 \n  55 permit eigrp any any precedence flash fragments time-range RANGE log \n  65 permit tcp any any precedence routine \n  70 permit tcp any any precedence routine \nip access-list POLICY\n  10 permit 23 any any \nip access-list TWO\n  2 remark this is a test string\n  4 permit eigrp any any \n  10 permit tcp 1.1.1.1/32 eq www any established log \n  20 permit tcp 1.1.1.1/32 any \ntime-range RANGE\ntime-range TEIMER\nvtp domain ntc\nsnmp-server user jay network-operator auth md5 0xe3b9e394dff8a08e8dbfef2c3f9a6564 priv 0xe3b9e394dff8a08e8dbfef2c3f9a6564 localizedkey\nsnmp-server user ntc network-admin auth md5 0x779969ac744909382f0c4bf39275a2c3 priv 0x779969ac744909382f0c4bf39275a2c3 localizedkey\nsnmp-server user netauto network-admin auth md5 0xd85b615bbd22469d476b571844afe9e6 priv 0xd85b615bbd22469d476b571844afe9e6 localizedkey\nrmon event 1 log trap public description FATAL(1) owner PMON@FATAL\nrmon event 2 log trap public description CRITICAL(2) owner PMON@CRITICAL\nrmon event 3 log trap public description ERROR(3) owner PMON@ERROR\nrmon event 4 log trap public description WARNING(4) owner PMON@WARNING\nrmon event 5 log trap public description INFORMATION(5) owner PMON@INFO\nno snmp-server enable traps entity entity_mib_change\nno snmp-server enable traps entity entity_module_status_change\nno snmp-server enable traps entity entity_power_status_change\nno snmp-server enable traps entity entity_module_inserted\nno snmp-server enable traps entity entity_module_removed\nno snmp-server enable traps entity entity_unrecognised_module\nno snmp-server enable traps entity entity_fan_status_change\nno snmp-server enable traps entity entity_power_out_change\nno snmp-server enable traps link linkDown\nno snmp-server enable traps link linkUp\nno snmp-server enable traps link extended-linkDown\nno snmp-server enable traps link extended-linkUp\nno snmp-server enable traps link cieLinkDown\nno snmp-server enable traps link cieLinkUp\nno snmp-server enable traps link delayed-link-state-change\nno snmp-server enable traps rf redundancy_framework\nno snmp-server enable traps license notify-license-expiry\nno snmp-server enable traps license notify-no-license-for-feature\nno snmp-server enable traps license notify-licensefile-missing\nno snmp-server enable traps license notify-license-expiry-warning\nno snmp-server enable traps upgrade UpgradeOpNotifyOnCompletion\nno snmp-server enable traps upgrade UpgradeJobStatusNotify\nno snmp-server enable traps rmon risingAlarm\nno snmp-server enable traps rmon fallingAlarm\nno snmp-server enable traps rmon hcRisingAlarm\nno snmp-server enable traps rmon hcFallingAlarm\nno snmp-server enable traps entity entity_sensor\nno snmp-server enable traps entity cefcMIBEnableStatusNotification\nsnmp-server community networktocode group network-operator\nntp server 33.33.33.33 prefer key 32\nntp server 192.0.2.10 use-vrf ntc\nntp peer 2001:db8::4101\nntp authentication-key 42 md5 qpg 7\nntp trusted-key 42\nntp logging\nntp master 8\naaa authentication login console none \nip route 1.1.1.0/24 2.2.2.2 tag 90 80\nip route 1.1.1.1/32 10.1.10.2\nip route 1.1.1.1/32 10.10.10.1\nip route 1.1.1.1/32 10.10.20.1\nip pim ssm range 232.0.0.0/8\nno ip igmp snooping\nvlan 1-20,30,33,40,100-105,333,400-401\nvlan 2\n  name native\nvlan 10\n  name test_segment\nvlan 20\n  name peer_keepalive\nvlan 30\n  name Puppet\nvlan 33\n  name PuppetAnsible\nvlan 333\n  name webvlan\nvlan 400\n  name db_vlan\nvlan 401\n  name dba_vlan\nservice dhcp\nip dhcp relay\nipv6 dhcp relay\nvrf context TESTING\nvrf context TestVRF\n  shutdown\nvrf context keepalive\nvrf context management\n  ip domain-name ntc.com\n  ip name-server 208.67.222.222\n  ip route 0.0.0.0/0 10.1.100.1\nvrf context test\ninterface Vlan1\n  mtu 1600\ninterface Vlan10\n  no shutdown\n  mtu 1600\n  vrf member ntc\n  hsrp version 2\ninterface Vlan20\n  no shutdown\n  mtu 1600\n  vrf member keepalive\n  ip address 10.1.20.3/24\ninterface Vlan100\n  mtu 1600\n  no ip redirects\n  ip address 20.20.20.2/24\n  ip address 100.100.100.2/24 secondary\ninterface Vlan233\n  mtu 1600\ninterface port-channel11\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\ninterface port-channel12\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  spanning-tree port type network\ninterface port-channel100\n  mtu 9216\n  lacp min-links 2\ninterface Ethernet1/1\ninterface Ethernet1/2\ninterface Ethernet1/3\ninterface Ethernet1/4\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\ninterface Ethernet1/5\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\ninterface Ethernet1/6\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 11 mode active\ninterface Ethernet1/7\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 11 mode active\ninterface Ethernet1/8\ninterface Ethernet1/9\ninterface Ethernet1/10\ninterface Ethernet1/11\ninterface Ethernet1/12\ninterface Ethernet1/13\ninterface Ethernet1/14\ninterface Ethernet1/15\ninterface Ethernet1/16\ninterface Ethernet1/17\ninterface Ethernet1/18\ninterface Ethernet1/19\ninterface Ethernet1/20\ninterface Ethernet1/21\ninterface Ethernet1/22\ninterface Ethernet1/23\ninterface Ethernet1/24\ninterface Ethernet1/25\ninterface Ethernet1/26\ninterface Ethernet1/27\ninterface Ethernet1/28\n  mtu 9216\n  channel-group 100 mode active\ninterface Ethernet1/29\n  mtu 9216\n  channel-group 100 mode active\ninterface Ethernet1/30\n  ip access-group ONE in\ninterface Ethernet1/31\n  ip access-group POLICY out\n  no switchport\n  mtu 1700\ninterface Ethernet1/32\n  no switchport\n  mtu 1600\n  ip pim sparse-mode\n  ip igmp version 2\n  ip igmp startup-query-interval 31\n  ip igmp startup-query-count 2\n  ip igmp static-oif route-map ANOTHER_TEST\n  no shutdown\ninterface Ethernet1/33\n  ip access-group ONE in\n  no switchport\n  mtu 1600\n  ip pim sparse-mode\n  ip igmp static-oif 236.0.0.0\n  ip igmp static-oif 237.0.0.0\n  ip igmp static-oif 238.0.0.0\n  ip igmp static-oif 239.0.0.0 source 1.1.1.1\n  no shutdown\ninterface Ethernet1/34\ninterface Ethernet1/35\ninterface Ethernet1/36\ninterface Ethernet1/37\ninterface Ethernet1/38\ninterface Ethernet1/39\ninterface Ethernet1/40\ninterface Ethernet1/41\ninterface Ethernet1/42\ninterface Ethernet1/43\ninterface Ethernet1/44\ninterface Ethernet1/45\ninterface Ethernet1/46\ninterface Ethernet1/47\ninterface Ethernet1/48\ninterface Ethernet2/1\n  no switchport\n  vrf member ntc\n  ip address 10.1.100.13/24\n  no shutdown\ninterface Ethernet2/2\n  no switchport\n  mtu 1600\n  ip address 10.10.60.1/24\n  no shutdown\ninterface Ethernet2/3\n  no switchport\n  mtu 1600\n  ip address 10.10.70.1/24\n  no shutdown\ninterface Ethernet2/4\n  no switchport\n  mtu 1600\n  ip address 10.10.80.1/24\n  no shutdown\ninterface Ethernet2/5\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 12 mode active\ninterface Ethernet2/6\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 12 mode active\ninterface Ethernet2/7\ninterface Ethernet2/8\ninterface Ethernet2/9\ninterface Ethernet2/10\ninterface Ethernet2/11\n  shutdown\ninterface Ethernet2/12\n  shutdown\ninterface mgmt0\n  description out of band mgmt interface\n  ip access-group INBOUND_MGMT in\n  vrf member management\n  ip address 10.1.100.21/24\ninterface loopback10\n  vrf member ntc\ninterface loopback11\n  vrf member ntc\n  ip address 11.11.11.11/24\ninterface loopback13\n  ip address 13.13.13.13/24\ninterface loopback15\n  vrf member test\ninterface loopback16\ncli alias name puppetoper show puppet agent oper\ncli alias name puppetshow show puppet agent last-exec-log\ncli alias name puppetdump show puppet config\ncli alias name puppetfacter show puppet facter\ncli alias name puppetrun execute puppet agent-oneshot\ncli alias name puppetconfig show run | sec puppet\ncli alias name puppetexecute execute puppet agent-oneshot\nline console\nline vty\n  session-limit 16\n  exec-timeout 0\nboot nxos bootflash:/nxos.7.0.3.I2.1.bin \n'

        self.assertEqual(result, expected)

    def test_backup_running_config(self):
        temp_file = NamedTemporaryFile()
        self.device.backup_running_config(temp_file.name)

        expected = '!Command: show running-config\n!Time: Tue Mar 22 21:23:11 2016\nversion 7.0(3)I2(1)\nhostname N9K2\nvdc N9K2 id 1\n  limit-resource vlan minimum 16 maximum 4094\n  limit-resource vrf minimum 2 maximum 4096\n  limit-resource port-channel minimum 0 maximum 511\n  limit-resource u4route-mem minimum 248 maximum 248\n  limit-resource u6route-mem minimum 96 maximum 96\n  limit-resource m4route-mem minimum 58 maximum 58\n  limit-resource m6route-mem minimum 8 maximum 8\nfeature telnet\nfeature nxapi\nfeature bash-shell\nfeature scp-server\nfeature vrrp\nfeature tacacs+\ncfs eth distribute\nfeature pim\nfeature udld\nfeature interface-vlan\nfeature hsrp\nfeature lacp\nfeature dhcp\nfeature vpc\nfeature lldp\nfeature vtp\nonep\n  session key-required enabled\nno password strength-check\nusername admin password 5 $1$6Anve29g$aKsAE8iRKAQzY7sW1qKZh0  role network-admin\nusername cisco password 5 $1$nGd5VWnS$LJ/a9ztNEt6xruMCG2Erl/  role network-admin\nusername jay password 5 $1$K6cIEEfy$vkYaWr5tEdgr55C86b74u/  role network-operator\nusername ntc password 5 $1$0WWXa9uW$EnQSp3nRPD.nIZTqAE//11  role network-admin\nusername netauto password 5 $1$ITxT/Gi0$QbHUtgzTCFt39i4FYSuzl1  role network-admin\nnxapi http port 80\nnxapi https port 443\nbanner motd *\nDISCONNECT FROM DEVICE IMMEDIATELY.\nIF YOU CONTINUE, YOU WILL BE PROSECUTED TO THE FULLEST\nEXTENT OF THE LAW!!!!\n*\nssh login-attempts 10\nip domain-lookup\nip domain-name ntc.com\nip name-server 208.67.222.222\nip host puppet 176.126.88.189\ntacacs-server timeout 10\ntacacs-server deadtime 30\ntacacs-server host 5.6.7.8 \ntacacs-server host 1.2.3.4 key 7 "\\"hello\\"" \nradius-server host 1.2.3.4 authentication accounting \nobject-group ip address OBJECTGROUP-IP\n  10 1.1.1.1/24 \n  20 2.2.2.2/24 \nip access-list INBOUND_MGMT\n  statistics per-entry\n  20 permit tcp 63.118.185.0/24 10.1.100.21/32 eq 22 \n  30 permit icmp any 10.1.100.21/32 \n  40 permit tcp any 10.1.100.21/32 eq 443 \n  50 permit tcp any 10.1.100.21/32 eq www \n  60 permit ip 10.1.100.0/24 10.1.100.21/32 \n  80 permit tcp 89.101.133.0/24 10.1.100.21/32 eq 22 \n  90 permit udp any 10.1.100.21/32 eq snmp \n  100 permit udp any 10.1.100.20/32 eq snmp \n  110 permit tcp 79.52.99.64/32 10.1.100.21/32 eq 22 \n  120 permit tcp 176.126.88.189/32 10.1.100.21/32 eq 22 \nip access-list MYACL\n  10 permit tcp 1.1.1.1/32 eq www any established log \n  20 deny udp 2.1.1.1/20 neq 80 5.5.5.0/24 eq 443 \n  40 remark COMMENT REMARK BY ANSIBLE\n  100 permit ip 10.1.1.1/32 100.1.1.1/24 log \nip access-list ONE\n  15 deny eigrp 1.1.1.1/32 2.2.2.2/32 \n  30 permit tcp any gt smtp any lt 33 urg ack psh rst syn fin established dscp cs7 log \n  40 permit eigrp any any precedence flash fragments time-range RANGE log \n  50 permit udp any range 10 20 any dscp af11 \n  55 permit eigrp any any precedence flash fragments time-range RANGE log \n  65 permit tcp any any precedence routine \n  70 permit tcp any any precedence routine \nip access-list POLICY\n  10 permit 23 any any \nip access-list TWO\n  2 remark this is a test string\n  4 permit eigrp any any \n  10 permit tcp 1.1.1.1/32 eq www any established log \n  20 permit tcp 1.1.1.1/32 any \ntime-range RANGE\ntime-range TEIMER\nvtp domain ntc\nsnmp-server user jay network-operator auth md5 0xe3b9e394dff8a08e8dbfef2c3f9a6564 priv 0xe3b9e394dff8a08e8dbfef2c3f9a6564 localizedkey\nsnmp-server user ntc network-admin auth md5 0x779969ac744909382f0c4bf39275a2c3 priv 0x779969ac744909382f0c4bf39275a2c3 localizedkey\nsnmp-server user netauto network-admin auth md5 0xd85b615bbd22469d476b571844afe9e6 priv 0xd85b615bbd22469d476b571844afe9e6 localizedkey\nrmon event 1 log trap public description FATAL(1) owner PMON@FATAL\nrmon event 2 log trap public description CRITICAL(2) owner PMON@CRITICAL\nrmon event 3 log trap public description ERROR(3) owner PMON@ERROR\nrmon event 4 log trap public description WARNING(4) owner PMON@WARNING\nrmon event 5 log trap public description INFORMATION(5) owner PMON@INFO\nno snmp-server enable traps entity entity_mib_change\nno snmp-server enable traps entity entity_module_status_change\nno snmp-server enable traps entity entity_power_status_change\nno snmp-server enable traps entity entity_module_inserted\nno snmp-server enable traps entity entity_module_removed\nno snmp-server enable traps entity entity_unrecognised_module\nno snmp-server enable traps entity entity_fan_status_change\nno snmp-server enable traps entity entity_power_out_change\nno snmp-server enable traps link linkDown\nno snmp-server enable traps link linkUp\nno snmp-server enable traps link extended-linkDown\nno snmp-server enable traps link extended-linkUp\nno snmp-server enable traps link cieLinkDown\nno snmp-server enable traps link cieLinkUp\nno snmp-server enable traps link delayed-link-state-change\nno snmp-server enable traps rf redundancy_framework\nno snmp-server enable traps license notify-license-expiry\nno snmp-server enable traps license notify-no-license-for-feature\nno snmp-server enable traps license notify-licensefile-missing\nno snmp-server enable traps license notify-license-expiry-warning\nno snmp-server enable traps upgrade UpgradeOpNotifyOnCompletion\nno snmp-server enable traps upgrade UpgradeJobStatusNotify\nno snmp-server enable traps rmon risingAlarm\nno snmp-server enable traps rmon fallingAlarm\nno snmp-server enable traps rmon hcRisingAlarm\nno snmp-server enable traps rmon hcFallingAlarm\nno snmp-server enable traps entity entity_sensor\nno snmp-server enable traps entity cefcMIBEnableStatusNotification\nsnmp-server community networktocode group network-operator\nntp server 33.33.33.33 prefer key 32\nntp server 192.0.2.10 use-vrf ntc\nntp peer 2001:db8::4101\nntp authentication-key 42 md5 qpg 7\nntp trusted-key 42\nntp logging\nntp master 8\naaa authentication login console none \nip route 1.1.1.0/24 2.2.2.2 tag 90 80\nip route 1.1.1.1/32 10.1.10.2\nip route 1.1.1.1/32 10.10.10.1\nip route 1.1.1.1/32 10.10.20.1\nip pim ssm range 232.0.0.0/8\nno ip igmp snooping\nvlan 1-20,30,33,40,100-105,333,400-401\nvlan 2\n  name native\nvlan 10\n  name test_segment\nvlan 20\n  name peer_keepalive\nvlan 30\n  name Puppet\nvlan 33\n  name PuppetAnsible\nvlan 333\n  name webvlan\nvlan 400\n  name db_vlan\nvlan 401\n  name dba_vlan\nservice dhcp\nip dhcp relay\nipv6 dhcp relay\nvrf context TESTING\nvrf context TestVRF\n  shutdown\nvrf context keepalive\nvrf context management\n  ip domain-name ntc.com\n  ip name-server 208.67.222.222\n  ip route 0.0.0.0/0 10.1.100.1\nvrf context test\ninterface Vlan1\n  mtu 1600\ninterface Vlan10\n  no shutdown\n  mtu 1600\n  vrf member ntc\n  hsrp version 2\ninterface Vlan20\n  no shutdown\n  mtu 1600\n  vrf member keepalive\n  ip address 10.1.20.3/24\ninterface Vlan100\n  mtu 1600\n  no ip redirects\n  ip address 20.20.20.2/24\n  ip address 100.100.100.2/24 secondary\ninterface Vlan233\n  mtu 1600\ninterface port-channel11\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\ninterface port-channel12\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  spanning-tree port type network\ninterface port-channel100\n  mtu 9216\n  lacp min-links 2\ninterface Ethernet1/1\ninterface Ethernet1/2\ninterface Ethernet1/3\ninterface Ethernet1/4\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\ninterface Ethernet1/5\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\ninterface Ethernet1/6\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 11 mode active\ninterface Ethernet1/7\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 11 mode active\ninterface Ethernet1/8\ninterface Ethernet1/9\ninterface Ethernet1/10\ninterface Ethernet1/11\ninterface Ethernet1/12\ninterface Ethernet1/13\ninterface Ethernet1/14\ninterface Ethernet1/15\ninterface Ethernet1/16\ninterface Ethernet1/17\ninterface Ethernet1/18\ninterface Ethernet1/19\ninterface Ethernet1/20\ninterface Ethernet1/21\ninterface Ethernet1/22\ninterface Ethernet1/23\ninterface Ethernet1/24\ninterface Ethernet1/25\ninterface Ethernet1/26\ninterface Ethernet1/27\ninterface Ethernet1/28\n  mtu 9216\n  channel-group 100 mode active\ninterface Ethernet1/29\n  mtu 9216\n  channel-group 100 mode active\ninterface Ethernet1/30\n  ip access-group ONE in\ninterface Ethernet1/31\n  ip access-group POLICY out\n  no switchport\n  mtu 1700\ninterface Ethernet1/32\n  no switchport\n  mtu 1600\n  ip pim sparse-mode\n  ip igmp version 2\n  ip igmp startup-query-interval 31\n  ip igmp startup-query-count 2\n  ip igmp static-oif route-map ANOTHER_TEST\n  no shutdown\ninterface Ethernet1/33\n  ip access-group ONE in\n  no switchport\n  mtu 1600\n  ip pim sparse-mode\n  ip igmp static-oif 236.0.0.0\n  ip igmp static-oif 237.0.0.0\n  ip igmp static-oif 238.0.0.0\n  ip igmp static-oif 239.0.0.0 source 1.1.1.1\n  no shutdown\ninterface Ethernet1/34\ninterface Ethernet1/35\ninterface Ethernet1/36\ninterface Ethernet1/37\ninterface Ethernet1/38\ninterface Ethernet1/39\ninterface Ethernet1/40\ninterface Ethernet1/41\ninterface Ethernet1/42\ninterface Ethernet1/43\ninterface Ethernet1/44\ninterface Ethernet1/45\ninterface Ethernet1/46\ninterface Ethernet1/47\ninterface Ethernet1/48\ninterface Ethernet2/1\n  no switchport\n  vrf member ntc\n  ip address 10.1.100.13/24\n  no shutdown\ninterface Ethernet2/2\n  no switchport\n  mtu 1600\n  ip address 10.10.60.1/24\n  no shutdown\ninterface Ethernet2/3\n  no switchport\n  mtu 1600\n  ip address 10.10.70.1/24\n  no shutdown\ninterface Ethernet2/4\n  no switchport\n  mtu 1600\n  ip address 10.10.80.1/24\n  no shutdown\ninterface Ethernet2/5\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 12 mode active\ninterface Ethernet2/6\n  switchport mode trunk\n  switchport trunk native vlan 2\n  switchport trunk allowed vlan 2-20\n  channel-group 12 mode active\ninterface Ethernet2/7\ninterface Ethernet2/8\ninterface Ethernet2/9\ninterface Ethernet2/10\ninterface Ethernet2/11\n  shutdown\ninterface Ethernet2/12\n  shutdown\ninterface mgmt0\n  description out of band mgmt interface\n  ip access-group INBOUND_MGMT in\n  vrf member management\n  ip address 10.1.100.21/24\ninterface loopback10\n  vrf member ntc\ninterface loopback11\n  vrf member ntc\n  ip address 11.11.11.11/24\ninterface loopback13\n  ip address 13.13.13.13/24\ninterface loopback15\n  vrf member test\ninterface loopback16\ncli alias name puppetoper show puppet agent oper\ncli alias name puppetshow show puppet agent last-exec-log\ncli alias name puppetdump show puppet config\ncli alias name puppetfacter show puppet facter\ncli alias name puppetrun execute puppet agent-oneshot\ncli alias name puppetconfig show run | sec puppet\ncli alias name puppetexecute execute puppet agent-oneshot\nline console\nline vty\n  session-limit 16\n  exec-timeout 0\nboot nxos bootflash:/nxos.7.0.3.I2.1.bin \n'
        contents = temp_file.read()

        self.assertEqual(contents, expected)

    def test_facts(self):
        self.assertEqual(hasattr(self.device, '_facts'), False)

        expected = {'uptime_string': '07:05:47:10', 'uptime': 625630, 'vlans': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '30', '33', '40', '100', '101', '102', '103', '104', '105', '333', '400', '401'], u'os_version': '7.0(3)I2(1)', u'serial_number': 'SAL1819S6BE', u'model': 'Nexus9000 C9396PX Chassis', u'hostname': 'N9K2', 'interfaces': ['mgmt0', 'Ethernet1/1', 'Ethernet1/2', 'Ethernet1/3', 'Ethernet1/4', 'Ethernet1/5', 'Ethernet1/6', 'Ethernet1/7', 'Ethernet1/8', 'Ethernet1/9', 'Ethernet1/10', 'Ethernet1/11', 'Ethernet1/12', 'Ethernet1/13', 'Ethernet1/14', 'Ethernet1/15', 'Ethernet1/16', 'Ethernet1/17', 'Ethernet1/18', 'Ethernet1/19', 'Ethernet1/20', 'Ethernet1/21', 'Ethernet1/22', 'Ethernet1/23', 'Ethernet1/24', 'Ethernet1/25', 'Ethernet1/26', 'Ethernet1/27', 'Ethernet1/28', 'Ethernet1/29', 'Ethernet1/30', 'Ethernet1/31', 'Ethernet1/32', 'Ethernet1/33', 'Ethernet1/34', 'Ethernet1/35', 'Ethernet1/36', 'Ethernet1/37', 'Ethernet1/38', 'Ethernet1/39', 'Ethernet1/40', 'Ethernet1/41', 'Ethernet1/42', 'Ethernet1/43', 'Ethernet1/44', 'Ethernet1/45', 'Ethernet1/46', 'Ethernet1/47', 'Ethernet1/48', 'Ethernet2/1', 'Ethernet2/2', 'Ethernet2/3', 'Ethernet2/4', 'Ethernet2/5', 'Ethernet2/6', 'Ethernet2/7', 'Ethernet2/8', 'Ethernet2/9', 'Ethernet2/10', 'Ethernet2/11', 'Ethernet2/12', 'port-channel11', 'port-channel12', 'port-channel100', 'loopback10', 'loopback11', 'loopback13', 'loopback15', 'loopback16', 'Vlan1', 'Vlan10', 'Vlan20', 'Vlan100', 'Vlan233'], 'fqdn': 'N/A'}

        self.assertEqual(self.device.facts, expected)
        self.assertEqual(hasattr(self.device, '_facts'), True) # caching test
        self.assertEqual(self.device.facts, expected) # caching test








#    def test_config(self):
#        command = 'interface Eth1'
#        result = self.device.config(command)
#
#        self.assertIsNone(result)
#        self.device.native.config.assert_called_with([command])
#
#    def test_bad_config(self):
#        command = 'asdf poknw'
#
#        with self.assertRaisesRegexp(CommandError, command):
#            self.device.config(command)
#
#    def test_config_list(self):
#        commands = ['interface Eth1', 'no shutdown']
#        result = self.device.config_list(commands)
#
#        self.assertIsNone(result)
#        self.device.native.config.assert_called_with(commands)
#
#    def test_bad_config_list(self):
#        commands = ['interface Eth1', 'apons']
#
#        with self.assertRaisesRegexp(CommandListError, commands[1]):
#            self.device.config_list(commands)
#
#    def test_show(self):
#        command = 'show ip arp'
#        result = self.device.show(command)
#
#        self.assertIsInstance(result, dict)
#        self.assertNotIn('command', result)
#        self.assertIn('dynamicEntries', result)
#
#        self.device.native.enable.assert_called_with(
#            [command], encoding='json')
#
#    def test_bad_show(self):
#        command = 'show microsoft'
#        with self.assertRaises(CommandError):
#            self.device.show(command)
#
#    def test_show_raw_text(self):
#        command = 'show hostname'
#        result = self.device.show(command, raw_text=True)
#
#        self.assertIsInstance(result, str)
#        self.assertEqual(result,
#                          'Hostname: spine1\nFQDN:     spine1.ntc.com\n')
#        self.device.native.enable.assert_called_with([command], encoding='text')
#
#    def test_show_list(self):
#        commands = ['show hostname', 'show clock']
#
#        result = self.device.show_list(commands)
#        self.assertIsInstance(result, list)
#
#        self.assertIn('hostname', result[0])
#        self.assertIn('fqdn', result[0])
#        self.assertIn('output', result[1])
#
#        self.device.native.enable.assert_called_with(commands, encoding='json')
#
#    def test_bad_show_list(self):
#        commands = ['show badcommand', 'show clock']
#        with self.assertRaisesRegexp(CommandListError, 'show badcommand'):
#            self.device.show_list(commands)
#
#    def test_save(self):
#        result = self.device.save()
#        self.assertTrue(result)
#        self.device.native.enable.assert_called_with(['copy running-config startup-config'], encoding='json')
#
#    @mock.patch.object(EOSFileCopy, 'remote_file_exists', autospec=True)
#    def test_file_copy_remote_exists(self, mock_fc):
#        mock_fc.return_value = True
#        result = self.device.file_copy_remote_exists('source_file')
#
#        self.assertTrue(result)
#
#    @mock.patch.object(EOSFileCopy, 'remote_file_exists', autospec=True)
#    def test_file_copy_remote_exists_failure(self, mock_fc):
#        mock_fc.return_value = False
#        result = self.device.file_copy_remote_exists('source_file')
#
#        self.assertFalse(result)
#
#    @mock.patch('pyntc.devices.eos_device.EOSFileCopy', autospec=True)
#    def test_file_copy(self, mock_fc):
#        instance = mock_fc.return_value
#        self.device.file_copy('source_file')
#
#        instance.send.assert_called_with()
#
#    def test_reboot(self):
#        self.device.reboot(confirm=True)
#        self.device.native.enable.assert_called_with(['reload now'], encoding='json')
#
#    def test_reboot_no_confirm(self):
#        self.device.reboot()
#        assert not self.device.native.enable.called
#
#    def test_reboot_with_timer(self):
#        with self.assertRaises(RebootTimerError):
#            self.device.reboot(confirm=True, timer=3)
#
#    def test_get_boot_options(self):
#        boot_options = self.device.get_boot_options()
#        self.assertEqual(boot_options, {'sys': 'EOS.swi'})
#
#    def test_set_boot_options(self):
#        self.device.set_boot_options('new_image.swi')
#        self.device.native.enable.assert_called_with(['install source new_image.swi'], encoding='json')
#
#    def test_backup_running_config(self):
#        filename = 'local_running_config'
#        self.device.backup_running_config(filename)
#
#        with open(filename, 'r') as f:
#            contents = f.read()
#
#        self.assertEqual(contents, self.device.running_config)
#        os.remove(filename)
#
#    def test_rollback(self):
#        self.device.rollback('good_checkpoint')
#        self.device.native.enable.assert_called_with(['configure replace good_checkpoint force'], encoding='json')
#
#    def test_bad_rollback(self):
#        with self.assertRaises(RollbackError):
#            self.device.rollback('bad_checkpoint')
#
#    def test_checkpiont(self):
#        self.device.checkpoint('good_checkpoint')
#        self.device.native.enable.assert_called_with(['copy running-config good_checkpoint'], encoding='json')
#
#    @mock.patch.object(EOSVlans, 'get_list', autospec=True)
#    def test_facts(self, mock_vlan_list):
#        mock_vlan_list.return_value = ['1', '2', '10']
#        facts = self.device.facts
#        self.assertIsInstance(facts['uptime'], int)
#        self.assertIsInstance(facts['uptime_string'], str)
#
#        del facts['uptime']
#        del facts['uptime_string']
#
#        expected = {
#            'vendor': 'arista',
#            'os_version': '4.14.7M-2384414.4147M',
#            'interfaces': [
#                'Ethernet1',
#                'Ethernet2',
#                'Ethernet3',
#                'Ethernet4',
#                'Ethernet5',
#                'Ethernet6',
#                'Ethernet7',
#                'Ethernet8',
#                'Management1',
#            ],
#            'hostname': 'eos-spine1',
#            'fqdn': 'eos-spine1.ntc.com',
#            'serial_number': '',
#            'model': 'vEOS',
#            'vlans': ['1', '2', '10']
#        }
#        self.assertEqual(facts, expected)
#
#        self.device.native.enable.reset_mock()
#        facts = self.device.facts
#        self.assertEqual(facts, expected)
#        self.device.native.enable.assert_not_called()
#
#    def test_running_config(self):
#        expected = self.device.show('show running-config', raw_text=True)
#        self.assertEqual(self.device.running_config, expected)
#
#    def test_starting_config(self):
#        expected = self.device.show('show startup-config', raw_text=True)
#        self.assertEqual(self.device.startup_config, expected)


if __name__ == '__main__':
    unittest.main()
