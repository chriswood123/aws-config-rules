import boto3
import json


def evaluate_compliance(config_item, instance_id,
                        attribute_key, attribute_value):
    if config_item['resourceType'] != 'AWS::EC2::Instance':
        return 'NOT_APPLICABLE'

    client = boto3.client('ec2')
    instance = client.describe_instances(InstanceIds=[instance_id])
    attributes = instance['Reservations'][0]['Instances'][0]

    try:
        if attributes[attribute_key] == attribute_value:
            return 'COMPLIANT'
        else:
            return 'NON_COMPLIANT'
    except KeyError:
        # Non compliant if instance doesn't
        # have the specified AttributeKey
        return 'NON_COMPLIANT'


def lambda_handler(event, context):
    invoking_event = json.loads(event['invokingEvent'])
    rule_parameters = json.loads(event['ruleParameters'])
    attribute_key = rule_parameters['AttributeKey']
    attribute_value = rule_parameters['AttributeValue']
    config_item = invoking_event['configurationItem']

    instance_id = config_item['resourceId']
    compliance_value = evaluate_compliance(config_item,
                                           instance_id,
                                           attribute_key,
                                           attribute_value)

    config = boto3.client('config')
    resouce_type = config_item['resourceType']
    timestamp = config_item['configurationItemCaptureTime']
    response = config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': resouce_type,
                'ComplianceResourceId': instance_id,
                'ComplianceType': compliance_value,
                'OrderingTimestamp': timestamp
            }
        ],
        ResultToken=event['resultToken'])
