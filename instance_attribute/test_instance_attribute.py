import boto3
from moto import mock_ec2
from instance_attribute import evaluate_compliance

def test_not_ec2_instance():
    assert evaluate_compliance({'resourceType': 'notEC2'}, 'i-11', 'a', 'b') == 'NOT_APPLICABLE'

@mock_ec2
def test_is_compliant():
    mock_instance = boto3.client('ec2').run_instances(MaxCount=1, MinCount=1, InstanceType='t2.small')
    instance_id = mock_instance['Instances'][0]['InstanceId']

    assert evaluate_compliance(
        {'resourceType': 'AWS::EC2::Instance'},
        instance_id,
        'InstanceType',
        't2.small'
    ) == 'COMPLIANT'

@mock_ec2
def test_is_non_compliant():
    mock_instance = boto3.client('ec2').run_instances(MaxCount=1, MinCount=1, InstanceType='t2.small')
    instance_id = mock_instance['Instances'][0]['InstanceId']

    assert evaluate_compliance(
        {'resourceType': 'AWS::EC2::Instance'},
        instance_id,
        'InstanceType',
        'm3.medium'
    ) == 'NON_COMPLIANT'

@mock_ec2
def test_attribute_not_found():
    mock_instance = boto3.client('ec2').run_instances(MaxCount=1, MinCount=1, InstanceType='t2.small')
    instance_id = mock_instance['Instances'][0]['InstanceId']

    assert evaluate_compliance(
        {'resourceType': 'AWS::EC2::Instance'},
        instance_id,
        'FakeKey',
        'FakeValue'
    ) == 'NON_COMPLIANT'

@mock_ec2
def test_json_attribute_value():
    mock_instance = boto3.client('ec2').run_instances(MaxCount=1, MinCount=1)
    instance_id = mock_instance['Instances'][0]['InstanceId']

    assert evaluate_compliance(
        {'resourceType': 'AWS::EC2::Instance'},
        instance_id,
        'Monitoring',
        # Moto always returns monitoring disabled
        # when describing an instance
        {'State': 'disabled'}
    ) == 'COMPLIANT'