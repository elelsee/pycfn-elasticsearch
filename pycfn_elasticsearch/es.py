#
# AWS Elasticsearch Service Custom Resource
#

import sys
sys.path.insert(0, './vendored')
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

import boto3
import json
from pycfn_custom_resource.lambda_backed import CustomResource


def convert_type_bool(arg):
    return arg.lower() in ("yes", "true", "t", "1")


class ElasticsearchCustomResource(CustomResource):
    def __init__(self, event):
        super(ElasticsearchCustomResource, self).__init__(event)

    def create(self):
        client = boto3.client('es', region_name=self._region)
        domain_name = self._resourceproperties.get('DomainName')
        cluster_config = self._resourceproperties.get('ElasticsearchClusterConfig')
        ebs_options = self._resourceproperties.get('EBSOptions')
        access_policies = self._resourceproperties.get('AccessPolicies')
        snapshot_options = self._resourceproperties.get('SnapshotOptions')
        advanced_options = self._resourceproperties.get('AdvancedOptions')
        kwargs = { "DomainName" : str(domain_name).lower() }
        if cluster_config:
            if cluster_config.get('DedicatedMasterEnabled'):
                cluster_config['DedicatedMasterEnabled'] = convert_type_bool(cluster_config['DedicatedMasterEnabled'])
            if cluster_config.get('InstanceCount'):
                cluster_config['InstanceCount'] = int(cluster_config['InstanceCount'])
            if cluster_config.get('ZoneAwarenessEnabled'):
                cluster_config['ZoneAwarenessEnabled'] = convert_type_bool(cluster_config['ZoneAwarenessEnabled'])
        kwargs['ElasticsearchClusterConfig'] = cluster_config
        if ebs_options:
            if ebs_options.get('VolumeSize'):
                ebs_options['VolumeSize'] = int(ebs_options['VolumeSize'])
            if ebs_options.get('EBSEnabled'):
                ebs_options['EBSEnabled'] = convert_type_bool(ebs_options['EBSEnabled'])
        kwargs['EBSOptions'] = ebs_options
        kwargs['AccessPolicies'] = json.dumps(access_policies)
        if snapshot_options:
            kwargs['SnapshotOptions'] = snapshot_options
        if advanced_options:
            kwargs['AdvancedOptions'] = advanced_options
        print kwargs
        response = client.create_elasticsearch_domain(**kwargs)
        print response
        return response.get('DomainStatus')

    def update(self):
        client = boto3.client('es', region_name=self._region)
        domain_name = self._resourceproperties.get('DomainName')
        cluster_config = self._resourceproperties.get('ElasticsearchClusterConfig')
        ebs_options = self._resourceproperties.get('EBSOptions')
        access_policies = self._resourceproperties.get('AccessPolicies')
        snapshot_options = self._resourceproperties.get('SnapshotOptions')
        advanced_options = self._resourceproperties.get('AdvancedOptions')
        response = client.update_elasticsearch_domain(
            DomainName = domain_name,
            ElasticsearchClusterConfig = cluster_config,
            EBSOptions = ebs_options,
            AccessPolicies = access_policies,
            SnapshotOptions = snapshot_options,
            AdvancedOptions = advanced_options
        )
        return response.get('DomainStatus')

    def delete(self):
        client = boto3.client('es', region_name=self._region)
        domain_name = self._resourceproperties.get('DomainName')
        response = client.delete_elasticsearch_domain(DomainName = domain_name)
        return response.get('DomainStatus')


def lambda_handler(event, context):
    log.info("Received event : {}".format(event))
    resource = ElasticsearchCustomResource(event)
    resource.process_event()
    return { 'message': 'done' }
