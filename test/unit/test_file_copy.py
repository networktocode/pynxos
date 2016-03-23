import unittest
import mock
from tempfile import NamedTemporaryFile

from pynxos.features.file_copy import FileCopy, FileTransferError

class FileCopyTestCase(unittest.TestCase):

    @mock.patch('pynxos.device.Device', autospec=True)
    def setUp(self, mock_device):
        self.device = mock_device
        self.device.host = 'host'
        self.device.username = 'user'
        self.device.password = 'pass'
        self.fc = FileCopy(self.device, '/path/to/source_file')

    def test_init(self):
        self.assertEqual(self.fc.device, self.device)
        self.assertEqual(self.fc.src, '/path/to/source_file')
        self.assertEqual(self.fc.dst, 'source_file')
        self.assertEqual(self.fc.port, 22)
        self.assertEqual(self.fc.file_system, 'bootflash:')

    def test_get_remote_size(self):
        self.device.show.return_value = '       4096    Mar 15 17:06:51 2016  .rpmstore/\n       3651    May 19 18:26:19 2014  20140519_182619_poap_6121_init.log\n       3651    May 19 18:34:38 2014  20140519_183438_poap_5884_init.log\n      23167    Jul 11 19:55:32 2014  20140711_195320_poap_5884_init.log\n       3735    Oct 09 18:00:43 2015  20151009_180036_poap_6291_init.log\n       2826    Oct 12 20:17:32 2015  abc\n       7160    Oct 06 13:49:57 2015  cfg_flowtracker1\n       7123    Oct 08 19:26:48 2015  cfg_flowtracker1_2\n      89620    Oct 09 18:04:41 2015  clean_n9k2_all_cfg\n       2773    Oct 09 18:04:18 2015  clean_n9k2_cfg\n      17339    Oct 09 19:58:44 2015  clean_n9k2_cp\n      18203    Oct 12 19:41:21 2015  clean_n9k2_cp2\n      18118    Oct 12 21:03:57 2015  config_2015-10-12_17:03:46.308598\n      18118    Oct 12 21:03:58 2015  config_2015-10-12_17:03:47.338797\n      18118    Oct 12 21:04:03 2015  config_2015-10-12_17:03:52.012664\n      18118    Oct 12 21:06:17 2015  config_2015-10-12_17:06:05.026284\n      18118    Oct 12 21:07:03 2015  config_2015-10-12_17:06:50.357353\n      18118    Oct 12 21:08:13 2015  config_2015-10-12_17:08:01.145064\n      18118    Oct 12 21:12:55 2015  config_2015-10-12_17:12:43.603017\n      18118    Oct 12 21:13:38 2015  config_2015-10-12_17:13:25.476126\n      18098    Oct 12 21:14:40 2015  config_2015-10-12_17:14:29.411540\n      18118    Oct 12 21:14:43 2015  config_2015-10-12_17:14:32.442546\n      18099    Oct 12 21:14:46 2015  config_2015-10-12_17:14:35.595983\n      18118    Oct 12 21:16:03 2015  config_2015-10-12_17:15:51.501546\n      18118    Oct 12 21:16:20 2015  config_2015-10-12_17:16:09.478200\n      18118    Oct 12 21:16:21 2015  config_2015-10-12_17:16:10.613538\n      18099    Oct 12 21:16:25 2015  config_2015-10-12_17:16:13.730374\n      18118    Oct 12 21:16:30 2015  config_2015-10-12_17:16:18.856276\n      18118    Oct 12 21:16:36 2015  config_2015-10-12_17:16:24.817255\n       4096    Jan 11 20:00:40 2016  configs/\n       5365    Feb 05 15:57:55 2015  configs:jaay.cfg\n       5365    Feb 05 15:51:31 2015  configs:jay.cfg\n      18061    Oct 09 19:12:42 2015  cp_with_shutdown\n        154    Feb 19 21:33:05 2015  eth3.cfg\n         65    Feb 19 21:18:28 2015  eth_1_1.cfg\n       4096    Aug 10 18:54:09 2015  home/\n      18111    Oct 12 20:30:41 2015  initial.conf\n       4096    Mar 15 15:42:22 2016  lost+found/\n  309991424    May 19 18:23:41 2014  n9000-dk9.6.1.2.I2.1.bin\n  353457152    Nov 02 15:14:40 2014  n9000-dk9.6.1.2.I3.1.bin\n   37612335    Nov 02 15:20:00 2014  n9000-epld.6.1.2.I3.1.img\n       9888    Oct 08 18:35:39 2015  n9k1_cfg\n      73970    Oct 09 16:30:54 2015  n9k2_all_cfg\n       7105    Oct 08 19:48:41 2015  n9k2_cfg\n       7142    Oct 08 18:49:19 2015  n9k2_cfg_safe\n      21293    Oct 09 17:16:57 2015  n9k2_cp\n       4096    Aug 10 20:17:35 2015  netmiko/\n      18187    Oct 12 20:31:20 2015  new_typo.conf\n      17927    Oct 12 18:25:40 2015  newcpfile\n  535352320    Mar 15 15:39:31 2016  nxos.7.0.3.I2.1.bin\n       4096    Jan 28 15:33:36 2015  onep/\n       6079    Oct 06 14:46:33 2015  pn9k1_cfg.bak\n   54466560    Jan 28 12:48:30 2015  puppet-1.0.0-nx-os-SPA-k9.ova\n       9698    Sep 19 05:43:12 2014  sart\n       4096    Feb 05 15:15:30 2015  scriaspts/\n       4096    Feb 05 15:09:35 2015  scripts/\n       3345    Feb 19 21:04:50 2015  standardconfig.cfg\n      21994    Oct 23 15:32:18 2015  travis_ping\n      18038    Oct 12 19:32:17 2015  tshootcp\n       4096    Mar 15 15:48:59 2016  virt_strg_pool_bf_vdc_1/\n       4096    Jan 28 15:30:29 2015  virtual-instance/\n        125    Mar 15 15:48:12 2016  virtual-instance.conf\n       2068    Mar 16 09:58:23 2016  vlan.dat\nUsage for bootflash://sup-local\n 2425626624 bytes used\n19439792128 bytes free\n21865418752 bytes total\n'
        result = self.fc.get_remote_size()
        expected = 19439792128

        self.assertEqual(result, expected)
        self.device.show.assert_called_with('dir bootflash:', raw_text=True)

    @mock.patch('os.path.getsize')
    def test_enough_space(self, mock_getsize):
        self.device.show.return_value = '       4096    Mar 15 17:06:51 2016  .rpmstore/\n       3651    May 19 18:26:19 2014  20140519_182619_poap_6121_init.log\n       3651    May 19 18:34:38 2014  20140519_183438_poap_5884_init.log\n      23167    Jul 11 19:55:32 2014  20140711_195320_poap_5884_init.log\n       3735    Oct 09 18:00:43 2015  20151009_180036_poap_6291_init.log\n       2826    Oct 12 20:17:32 2015  abc\n       7160    Oct 06 13:49:57 2015  cfg_flowtracker1\n       7123    Oct 08 19:26:48 2015  cfg_flowtracker1_2\n      89620    Oct 09 18:04:41 2015  clean_n9k2_all_cfg\n       2773    Oct 09 18:04:18 2015  clean_n9k2_cfg\n      17339    Oct 09 19:58:44 2015  clean_n9k2_cp\n      18203    Oct 12 19:41:21 2015  clean_n9k2_cp2\n      18118    Oct 12 21:03:57 2015  config_2015-10-12_17:03:46.308598\n      18118    Oct 12 21:03:58 2015  config_2015-10-12_17:03:47.338797\n      18118    Oct 12 21:04:03 2015  config_2015-10-12_17:03:52.012664\n      18118    Oct 12 21:06:17 2015  config_2015-10-12_17:06:05.026284\n      18118    Oct 12 21:07:03 2015  config_2015-10-12_17:06:50.357353\n      18118    Oct 12 21:08:13 2015  config_2015-10-12_17:08:01.145064\n      18118    Oct 12 21:12:55 2015  config_2015-10-12_17:12:43.603017\n      18118    Oct 12 21:13:38 2015  config_2015-10-12_17:13:25.476126\n      18098    Oct 12 21:14:40 2015  config_2015-10-12_17:14:29.411540\n      18118    Oct 12 21:14:43 2015  config_2015-10-12_17:14:32.442546\n      18099    Oct 12 21:14:46 2015  config_2015-10-12_17:14:35.595983\n      18118    Oct 12 21:16:03 2015  config_2015-10-12_17:15:51.501546\n      18118    Oct 12 21:16:20 2015  config_2015-10-12_17:16:09.478200\n      18118    Oct 12 21:16:21 2015  config_2015-10-12_17:16:10.613538\n      18099    Oct 12 21:16:25 2015  config_2015-10-12_17:16:13.730374\n      18118    Oct 12 21:16:30 2015  config_2015-10-12_17:16:18.856276\n      18118    Oct 12 21:16:36 2015  config_2015-10-12_17:16:24.817255\n       4096    Jan 11 20:00:40 2016  configs/\n       5365    Feb 05 15:57:55 2015  configs:jaay.cfg\n       5365    Feb 05 15:51:31 2015  configs:jay.cfg\n      18061    Oct 09 19:12:42 2015  cp_with_shutdown\n        154    Feb 19 21:33:05 2015  eth3.cfg\n         65    Feb 19 21:18:28 2015  eth_1_1.cfg\n       4096    Aug 10 18:54:09 2015  home/\n      18111    Oct 12 20:30:41 2015  initial.conf\n       4096    Mar 15 15:42:22 2016  lost+found/\n  309991424    May 19 18:23:41 2014  n9000-dk9.6.1.2.I2.1.bin\n  353457152    Nov 02 15:14:40 2014  n9000-dk9.6.1.2.I3.1.bin\n   37612335    Nov 02 15:20:00 2014  n9000-epld.6.1.2.I3.1.img\n       9888    Oct 08 18:35:39 2015  n9k1_cfg\n      73970    Oct 09 16:30:54 2015  n9k2_all_cfg\n       7105    Oct 08 19:48:41 2015  n9k2_cfg\n       7142    Oct 08 18:49:19 2015  n9k2_cfg_safe\n      21293    Oct 09 17:16:57 2015  n9k2_cp\n       4096    Aug 10 20:17:35 2015  netmiko/\n      18187    Oct 12 20:31:20 2015  new_typo.conf\n      17927    Oct 12 18:25:40 2015  newcpfile\n  535352320    Mar 15 15:39:31 2016  nxos.7.0.3.I2.1.bin\n       4096    Jan 28 15:33:36 2015  onep/\n       6079    Oct 06 14:46:33 2015  pn9k1_cfg.bak\n   54466560    Jan 28 12:48:30 2015  puppet-1.0.0-nx-os-SPA-k9.ova\n       9698    Sep 19 05:43:12 2014  sart\n       4096    Feb 05 15:15:30 2015  scriaspts/\n       4096    Feb 05 15:09:35 2015  scripts/\n       3345    Feb 19 21:04:50 2015  standardconfig.cfg\n      21994    Oct 23 15:32:18 2015  travis_ping\n      18038    Oct 12 19:32:17 2015  tshootcp\n       4096    Mar 15 15:48:59 2016  virt_strg_pool_bf_vdc_1/\n       4096    Jan 28 15:30:29 2015  virtual-instance/\n        125    Mar 15 15:48:12 2016  virtual-instance.conf\n       2068    Mar 16 09:58:23 2016  vlan.dat\nUsage for bootflash://sup-local\n 2425626624 bytes used\n19439792128 bytes free\n21865418752 bytes total\n'
        mock_getsize.return_value = 10

        result = self.fc.enough_remote_space()

        self.assertEqual(result, True)
        mock_getsize.assert_called_with('/path/to/source_file')

    @mock.patch('os.path.getsize')
    def test_not_enough_space(self, mock_getsize):
        self.device.show.return_value = '       4096    Mar 15 17:06:51 2016  .rpmstore/\n       3651    May 19 18:26:19 2014  20140519_182619_poap_6121_init.log\n       3651    May 19 18:34:38 2014  20140519_183438_poap_5884_init.log\n      23167    Jul 11 19:55:32 2014  20140711_195320_poap_5884_init.log\n       3735    Oct 09 18:00:43 2015  20151009_180036_poap_6291_init.log\n       2826    Oct 12 20:17:32 2015  abc\n       7160    Oct 06 13:49:57 2015  cfg_flowtracker1\n       7123    Oct 08 19:26:48 2015  cfg_flowtracker1_2\n      89620    Oct 09 18:04:41 2015  clean_n9k2_all_cfg\n       2773    Oct 09 18:04:18 2015  clean_n9k2_cfg\n      17339    Oct 09 19:58:44 2015  clean_n9k2_cp\n      18203    Oct 12 19:41:21 2015  clean_n9k2_cp2\n      18118    Oct 12 21:03:57 2015  config_2015-10-12_17:03:46.308598\n      18118    Oct 12 21:03:58 2015  config_2015-10-12_17:03:47.338797\n      18118    Oct 12 21:04:03 2015  config_2015-10-12_17:03:52.012664\n      18118    Oct 12 21:06:17 2015  config_2015-10-12_17:06:05.026284\n      18118    Oct 12 21:07:03 2015  config_2015-10-12_17:06:50.357353\n      18118    Oct 12 21:08:13 2015  config_2015-10-12_17:08:01.145064\n      18118    Oct 12 21:12:55 2015  config_2015-10-12_17:12:43.603017\n      18118    Oct 12 21:13:38 2015  config_2015-10-12_17:13:25.476126\n      18098    Oct 12 21:14:40 2015  config_2015-10-12_17:14:29.411540\n      18118    Oct 12 21:14:43 2015  config_2015-10-12_17:14:32.442546\n      18099    Oct 12 21:14:46 2015  config_2015-10-12_17:14:35.595983\n      18118    Oct 12 21:16:03 2015  config_2015-10-12_17:15:51.501546\n      18118    Oct 12 21:16:20 2015  config_2015-10-12_17:16:09.478200\n      18118    Oct 12 21:16:21 2015  config_2015-10-12_17:16:10.613538\n      18099    Oct 12 21:16:25 2015  config_2015-10-12_17:16:13.730374\n      18118    Oct 12 21:16:30 2015  config_2015-10-12_17:16:18.856276\n      18118    Oct 12 21:16:36 2015  config_2015-10-12_17:16:24.817255\n       4096    Jan 11 20:00:40 2016  configs/\n       5365    Feb 05 15:57:55 2015  configs:jaay.cfg\n       5365    Feb 05 15:51:31 2015  configs:jay.cfg\n      18061    Oct 09 19:12:42 2015  cp_with_shutdown\n        154    Feb 19 21:33:05 2015  eth3.cfg\n         65    Feb 19 21:18:28 2015  eth_1_1.cfg\n       4096    Aug 10 18:54:09 2015  home/\n      18111    Oct 12 20:30:41 2015  initial.conf\n       4096    Mar 15 15:42:22 2016  lost+found/\n  309991424    May 19 18:23:41 2014  n9000-dk9.6.1.2.I2.1.bin\n  353457152    Nov 02 15:14:40 2014  n9000-dk9.6.1.2.I3.1.bin\n   37612335    Nov 02 15:20:00 2014  n9000-epld.6.1.2.I3.1.img\n       9888    Oct 08 18:35:39 2015  n9k1_cfg\n      73970    Oct 09 16:30:54 2015  n9k2_all_cfg\n       7105    Oct 08 19:48:41 2015  n9k2_cfg\n       7142    Oct 08 18:49:19 2015  n9k2_cfg_safe\n      21293    Oct 09 17:16:57 2015  n9k2_cp\n       4096    Aug 10 20:17:35 2015  netmiko/\n      18187    Oct 12 20:31:20 2015  new_typo.conf\n      17927    Oct 12 18:25:40 2015  newcpfile\n  535352320    Mar 15 15:39:31 2016  nxos.7.0.3.I2.1.bin\n       4096    Jan 28 15:33:36 2015  onep/\n       6079    Oct 06 14:46:33 2015  pn9k1_cfg.bak\n   54466560    Jan 28 12:48:30 2015  puppet-1.0.0-nx-os-SPA-k9.ova\n       9698    Sep 19 05:43:12 2014  sart\n       4096    Feb 05 15:15:30 2015  scriaspts/\n       4096    Feb 05 15:09:35 2015  scripts/\n       3345    Feb 19 21:04:50 2015  standardconfig.cfg\n      21994    Oct 23 15:32:18 2015  travis_ping\n      18038    Oct 12 19:32:17 2015  tshootcp\n       4096    Mar 15 15:48:59 2016  virt_strg_pool_bf_vdc_1/\n       4096    Jan 28 15:30:29 2015  virtual-instance/\n        125    Mar 15 15:48:12 2016  virtual-instance.conf\n       2068    Mar 16 09:58:23 2016  vlan.dat\nUsage for bootflash://sup-local\n 2425626624 bytes used\n19439792128 bytes free\n21865418752 bytes total\n'
        mock_getsize.return_value = 100000000000000000

        result = self.fc.enough_remote_space()

        self.assertEqual(result, False)
        mock_getsize.assert_called_with('/path/to/source_file')

    @mock.patch('os.path.isfile')
    def test_local_file_exists(self, mock_isfile):
        mock_isfile.return_value = True
        result = self.fc.local_file_exists()
        expected = True

        self.assertEqual(result, expected)
        mock_isfile.assert_called_with('/path/to/source_file')

    @mock.patch('os.path.isfile')
    def test_local_file_doesnt_exist(self, mock_isfile):
        mock_isfile.return_value = False
        result = self.fc.local_file_exists()
        expected = False

        self.assertEqual(result, expected)
        mock_isfile.assert_called_with('/path/to/source_file')

    @mock.patch.object(FileCopy, 'get_local_md5')
    def test_file_already_exists(self, mock_local_md5):
        mock_local_md5.return_value = 'b211e79fbaede5859ed2192b0fc5f1d5'
        self.device.show.return_value = {'file_content_md5sum': 'b211e79fbaede5859ed2192b0fc5f1d5\n'}

        result = self.fc.already_transfered()

        self.assertEqual(result, True)
        self.device.show.assert_called_with('show file bootflash:source_file md5sum', raw_text=False)
        mock_local_md5.assert_called_with()

    @mock.patch.object(FileCopy, 'get_local_md5')
    def test_file_doesnt_already_exists(self, mock_local_md5):
        mock_local_md5.return_value = 'abcdef12345'
        self.device.show.return_value = {'file_content_md5sum': 'b211e79fbaede5859ed2192b0fc5f1d5\n'}

        result = self.fc.already_transfered()

        self.assertEqual(result, False)
        self.device.show.assert_called_with('show file bootflash:source_file md5sum', raw_text=False)
        mock_local_md5.assert_called_with()

    def test_remote_file_doesnt_exists(self):
        self.device.show.return_value = 'No such file'

        result = self.fc.remote_file_exists()

        self.assertEqual(result, False)
        self.device.show.assert_called_with('dir bootflash:/source_file', raw_text=True)

    def test_remote_file_exists(self):
        self.device.show.return_value = '          5    Mar 23 00:48:15 2016  smallfile\nUsage for bootflash://sup-local\n 2425630720 bytes used\n19439788032 bytes free\n21865418752 bytes total\n'

        result = self.fc.remote_file_exists()

        self.assertEqual(result, True)
        self.device.show.assert_called_with('dir bootflash:/source_file', raw_text=True)

    @mock.patch('pynxos.features.file_copy.paramiko')
    @mock.patch('pynxos.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, 'get_local_md5')
    @mock.patch.object(FileCopy, 'get_remote_md5')
    @mock.patch.object(FileCopy, 'local_file_exists')
    @mock.patch.object(FileCopy, 'enough_space')
    def test_send_file(self, mock_enough_space, mock_local_file_exists, mock_remote_md5, mock_local_md5, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'abc'
        mock_local_file_exists.return_value = True
        mock_enough_space.return_value = True

        mock_ssh = mock_paramiko.SSHClient.return_value

        self.fc.send()

        mock_paramiko.SSHClient.assert_called_with()

        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
        mock_ssh.connect.assert_called_with(allow_agent=False,
                                             hostname=self.device.host,
                                             look_for_keys=False,
                                             password=self.device.password,
                                             port=22,
                                             username=self.device.username)

        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
        mock_SCP.return_value.put.assert_called_with('/path/to/source_file', 'bootflash:source_file')
        mock_SCP.return_value.close.assert_called_with()


    @mock.patch('pynxos.features.file_copy.paramiko')
    @mock.patch('pynxos.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, 'get_local_md5')
    @mock.patch.object(FileCopy, 'get_remote_md5')
    @mock.patch.object(FileCopy, 'local_file_exists')
    @mock.patch.object(FileCopy, 'enough_space')
    def test_get_file(self, mock_enough_space, mock_local_file_exists, mock_remote_md5, mock_local_md5, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'abc'
        mock_local_file_exists.return_value = True
        mock_enough_space.return_value = True

        mock_ssh = mock_paramiko.SSHClient.return_value

        self.fc.get()

        mock_paramiko.SSHClient.assert_called_with()

        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
        mock_ssh.connect.assert_called_with(allow_agent=False,
                                             hostname=self.device.host,
                                             look_for_keys=False,
                                             password=self.device.password,
                                             port=22,
                                             username=self.device.username)

        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
        mock_SCP.return_value.get.assert_called_with('bootflash:source_file', '/path/to/source_file')
        mock_SCP.return_value.close.assert_called_with()


    @mock.patch('pynxos.features.file_copy.paramiko')
    @mock.patch('pynxos.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, 'get_local_md5')
    @mock.patch.object(FileCopy, 'get_remote_md5')
    @mock.patch.object(FileCopy, 'local_file_exists')
    @mock.patch.object(FileCopy, 'enough_space')
    def test_send_file_error_local_not_exist(self, mock_enough_space, mock_local_file_exists, mock_remote_md5, mock_local_md5, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'abc'
        mock_local_file_exists.return_value = False
        mock_enough_space.return_value = True

        mock_ssh = mock_paramiko.SSHClient.return_value

        with self.assertRaises(FileTransferError):
            self.fc.send()

    @mock.patch('pynxos.features.file_copy.paramiko')
    @mock.patch('pynxos.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, 'get_local_md5')
    @mock.patch.object(FileCopy, 'get_remote_md5')
    @mock.patch.object(FileCopy, 'local_file_exists')
    @mock.patch.object(FileCopy, 'enough_space')
    def test_send_file_error_not_enough_space(self, mock_enough_space, mock_local_file_exists, mock_remote_md5, mock_local_md5, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'abc'
        mock_local_file_exists.return_value = True
        mock_enough_space.return_value = False

        mock_ssh = mock_paramiko.SSHClient.return_value

        with self.assertRaises(FileTransferError):
            self.fc.send()

    @mock.patch('pynxos.features.file_copy.paramiko')
    @mock.patch('pynxos.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, 'get_local_md5')
    @mock.patch.object(FileCopy, 'get_remote_md5')
    @mock.patch.object(FileCopy, 'local_file_exists')
    @mock.patch.object(FileCopy, 'enough_space')
    def test_send_file_transfer_error(self, mock_enough_space, mock_local_file_exists, mock_remote_md5, mock_local_md5, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'abc'
        mock_local_file_exists.return_value = True
        mock_enough_space.return_value = True

        mock_ssh = mock_paramiko.SSHClient.return_value
        mock_SCP.return_value.put.side_effect = Exception

        with self.assertRaises(FileTransferError):
            self.fc.send()

        mock_paramiko.SSHClient.assert_called_with()

        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
        mock_ssh.connect.assert_called_with(allow_agent=False,
                                             hostname=self.device.host,
                                             look_for_keys=False,
                                             password=self.device.password,
                                             port=22,
                                             username=self.device.username)

        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
        mock_SCP.return_value.put.assert_called_with('/path/to/source_file', 'bootflash:source_file')
        mock_SCP.return_value.close.assert_called_with()

#    @mock.patch('pyhpncw7.features.file_copy.paramiko')
#    @mock.patch('pyhpncw7.features.file_copy.SCPClient')
#    @mock.patch.object(FileCopy, '_safety_checks')
#    @mock.patch.object(FileCopy, '_get_local_md5')
#    @mock.patch.object(FileCopy, '_get_remote_md5')
#    def test_transfer_file_mismatch_hash(self, mock_remote_md5, mock_local_md5, mock_safety_checks, mock_SCP, mock_paramiko):
#        mock_remote_md5.return_value = 'abc'
#        mock_local_md5.return_value = 'def'
#
#        mock_ssh = mock_paramiko.SSHClient.return_value
#
#        with self.assertRaises(FileHashMismatchError):
#            self.file_copy.transfer_file()
#
#        mock_paramiko.SSHClient.assert_called_with()
#
#        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
#        mock_ssh.connect.assert_called_with(allow_agent=False,
#                                             hostname=self.device.host,
#                                             look_for_keys=False,
#                                             password=self.device.password,
#                                             port=22,
#                                             username=self.device.username)
#
#        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
#        mock_SCP.return_value.put.assert_called_with('/path/to/source/file.txt', 'flash:/file.txt')
#        mock_SCP.return_value.close.assert_called_with()
#
#    @mock.patch('pyhpncw7.features.file_copy.paramiko')
#    @mock.patch('pyhpncw7.features.file_copy.SCPClient')
#    @mock.patch.object(FileCopy, '_safety_checks')
#    @mock.patch.object(FileCopy, '_get_local_md5')
#    @mock.patch.object(FileCopy, '_get_remote_md5')
#    def test_transfer_file_error(self, mock_remote_md5, mock_local_md5, mock_safety_checks, mock_SCP, mock_paramiko):
#        mock_remote_md5.return_value = 'abc'
#        mock_local_md5.return_value = 'def'
#
#        mock_ssh = mock_paramiko.SSHClient.return_value
#
#        mock_SCP.return_value.put.side_effect = Exception
#
#        with self.assertRaises(FileTransferError):
#            self.file_copy.transfer_file()
#
#        mock_paramiko.SSHClient.assert_called_with()
#
#        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
#        mock_ssh.connect.assert_called_with(allow_agent=False,
#                                             hostname=self.device.host,
#                                             look_for_keys=False,
#                                             password=self.device.password,
#                                             port=22,
#                                             username=self.device.username)
#
#        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
#        mock_SCP.return_value.put.assert_called_with('/path/to/source/file.txt', 'flash:/file.txt')






if __name__ == "__main__":
    unittest.main()