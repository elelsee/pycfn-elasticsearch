
``` json
{
  "Type" : "Custom::ElasticsearchServiceDomain",
  "Properties" : {
    "ServiceToken": { 
        "Fn::Join": [ "", [ "arn:aws:lambda:", 
                    { "Ref": "AWS::Region" }, ":", 
                    { "Ref": "AWS::AccountId" }, ":function:", 
                    {"Ref" : "LambdaFunctionName"} ] ] },
    "DomainName" : String,
    "ElasticsearchClusterConfig" : {
        "InstanceType": String,
        "InstanceCount": Integer,
        "DedicatedMasterEnabled": Boolean,
        "ZoneAwarenessEnabled": Boolean,
        "DedicatedMasterType": String,
        "DedicatedMasterCount": Integer
    },
    "EBSOptions" : {
        "EBSEnabled": True,
        "VolumeType": String,
        "VolumeSize": Integer,
        "Iops": Integer
    },
    "AccessPolicies" : String,
    "SnapshotOptions" : {
        "AutomatedSnapshotStartHour": Integer
    },
    "AdvancedOptions" : {
        "rest.action.multi.allow_explicit" : String,
        "indices.fielddata.cache.size" : String
    }
  }
}
```

