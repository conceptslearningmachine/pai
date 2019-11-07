#!/usr/bin/env python
import copy
import logging


class InternalStorage(object):
    def __init__(self, cluster_conf, service_conf, default_service_conf):
        self.cluster_conf = cluster_conf
        self.service_conf = self.merge_service_configuration(default_service_conf, service_conf)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def merge_service_configuration(overwrite_srv_cfg, default_srv_cfg):
        if overwrite_srv_cfg is None:
            return default_srv_cfg
        srv_cfg = default_srv_cfg.copy()
        for k in overwrite_srv_cfg:
            srv_cfg[k] = overwrite_srv_cfg[k]
        return srv_cfg

    def validation_pre(self):
        type_ = self.service_conf.get('type', '')
        if type_ == 'hostPath':
            machine_list = self.cluster_conf['machine-list']
            if len([host for host in machine_list if host.get('pai-master') == 'true']) != 1:
                return False, '1 and only 1 "pai-master=true" machine is required to deploy the rest server'
            quotaGB = int(self.cluster_conf['quotaGB'])
            assert quotaGB >= 1
            return True, None
        else:
            return False, 'Unknown internal storage type {}'.format(type_)

    def run(self):
        result = copy.deepcopy(self.service_conf)
        if result['enable']:
            machine_list = self.cluster_conf['machine-list']
            master_ip = [host['hostip'] for host in machine_list if host.get('pai-master') == 'true'][0]
            result['masterIp'] = master_ip
            result['quotaGB'] = int(result['quotaGB'])
        return result

    def validation_post(self, conf):
        return True, None
