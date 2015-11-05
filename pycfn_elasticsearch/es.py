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
import random

from botocore.exceptions import ClientError
from pycfn_custom_resource.lambda_backed import CustomResource
from string import ascii_lowercase


def convert_type_bool(arg):
    return arg.lower() in ("yes", "true", "t", "1")


class ElasticsearchCustomResource(CustomResource):
    def __init__(self, event, context):
        super(ElasticsearchCustomResource, self).__init__(event, context)

    def describe_domain(self):
        client = boto3.client('es', region_name=self._region)
        domain_name = self.result_text.get('DomainName')
        domain_name = domain_name if domain_name else self.physicalresourceid
        try:
            response = client.describe_elasticsearch_domain(DomainName=domain_name)
            return response.get('DomainStatus')
        except ClientError:
            e = sys.exc_info()[1]
            message = e.response['Error']['Message']
            if self.requesttype == "Delete" and message.startswith('Domain not found'):
                return { 'Processing': False }
            else:
                raise

    def get_status(self):
        log.info(u"Polling status for %s-%s", self.logicalresourceid, self.requesttype)
        domain_status = self.describe_domain()
        processing = domain_status.get('Processing')
        if not processing:
            self.processing = False
        return self.result_text

    def get_domain_name(self):
        return ''.join(random.choice(ascii_lowercase) for _ in range(15))

    def create_es(self):
        domain_name = self._resourceproperties.get('DomainName')
        domain_name = domain_name if domain_name else self.get_domain_name()
        log.info(u"Command %s-%s using Domain Name %s", self.logicalresourceid, self.requesttype, domain_name)
        cluster_config = self._resourceproperties.get('ElasticsearchClusterConfig')
        ebs_options = self._resourceproperties.get('EBSOptions')
        access_policies = self._resourceproperties.get('AccessPolicies')
        snapshot_options = self._resourceproperties.get('SnapshotOptions')
        advanced_options = self._resourceproperties.get('AdvancedOptions')
        kwargs = { "DomainName" : domain_name }
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
        log.info(u"Command %s-%s sending: %s", self.logicalresourceid, self.requesttype, json.dumps(kwargs))
        client = boto3.client('es', region_name=self._region)
        response = client.create_elasticsearch_domain(**kwargs)
        self._physicalresourceid = domain_name
        self.processing = True
        return response.get('DomainStatus')

    def update_es(self):
        client = boto3.client('es', region_name=self._region)
        domain_name = self.result_text.get('DomainName')
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
        self.processing = True
        return response.get('DomainStatus')

    def delete_es(self):
        client = boto3.client('es', region_name=self._region)
        domain_name = self.physicalresourceid
        response = client.delete_elasticsearch_domain(DomainName = domain_name)
        self.processing = True
        return response.get('DomainStatus')

    def create(self):
        if self.processing:
            return self.get_status()
        else:
            return self.create_es()

    def update(self):
        if self.processing:
            return self.get_status()
        else:
            return self.update_es()

    def delete(self):
        if self.processing:
            return self.get_status()
        else:
            return self.delete_es()


def lambda_handler(event, context):
    log.info("Received event : {}".format(event))
    log.info("Event: {}".format(json.dumps(event)))

    context_json = context.__dict__
    context_json['remaining_time'] = context.get_remaining_time_in_millis()
    if 'identity' in context_json.keys():
        context_json.pop('identity')
    if 'client_context' in context_json.keys():
        context_json.pop('client_context')
    log.info("Context: {}".format(json.dumps(context_json)))

    resource = ElasticsearchCustomResource(event, context)
    resource.process_event()
    return { 'message': 'done' }
