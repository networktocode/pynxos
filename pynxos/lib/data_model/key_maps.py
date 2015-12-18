BASIC_FACTS_KEY_MAP = {
    u'os': u'rr_sys_ver',
    u'kickstart_image': u'kickstart_ver_str',
    u'platform': u'chassis_id',
    u'hostname': u'host_name',
    u'last_reboot_reason': u'rr_reason',
}

INTERFACE_KEY_MAP = {
    u'description': u'name',
}

MOD_INFO_KEY_MAP = {
    u'type': u'modtype',
}

PS_INFO_KEY_MAP = {
    u'number': u'psnum',
    u'model': u'psmodel',
    u'actual_output': u'actual_out',
    u'actual_input': u'actual_in',
    u'total_capacity': u'tot_capa',
    u'status': u'ps_status',
}

FAN_KEY_MAP = {
    u'name': u'fanname',
    u'model': u'fanmodel',
    u'hw_ver': u'fanhwver',
    u'direction': u'fandir',
    u'status': u'fanstatus',
}

VLAN_KEY_MAP = {
    'id': 'vlanshowbr-vlanid',
    'name': 'vlanshowbr-vlanname',
    'state': 'vlanshowbr-vlanstate',
    'admin_state': 'vlanshowbr-shutstate',
}