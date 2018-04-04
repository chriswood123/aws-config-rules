import boto3
import json

def evaluate_compliance(config_item, instance_id, attribute_key, attribute_value):
    if config_item['resourceType'] != 'AWS::EC2::Instance':
        return 'NOT_APPLICABLE'
    
    instance = boto3.client('ec2').describe_instances(InstanceIds=[instance_id])
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

    instance_id = invoking_event['configurationItem']['resourceId']
    compliance_value = evaluate_compliance(invoking_event['configurationItem'],
                                            instance_id,
                                            attribute_key,
                                            attribute_value)
    
    config = boto3.client('config')
    response = config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': invoking_event['configurationItem']['resourceType'],
                'ComplianceResourceId': instance_id,
                'ComplianceType': compliance_value,
                'OrderingTimestamp': invoking_event['configurationItem']['configurationItemCaptureTime']
            }
        ],
        ResultToken=event['resultToken'])