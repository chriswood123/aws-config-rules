import unittest
import boto3
from moto import mock_ec2
from instance_attribute import evaluate_compliance


@mock_ec2
class TestEvaluateCompliance(unittest.TestCase):

    def setUp(self):
        self.client = boto3.client('ec2')
        self.image_id = self.client.describe_images()['Images'][0]['ImageId']
        self.mock_instance = self.client.run_instances(
            MaxCount=1,
            MinCount=1,
            ImageId=self.image_id,
            InstanceType='t2.small'
        )
        self.instance_id = self.mock_instance['Instances'][0]['InstanceId']

    def test_not_ec2_instance(self):
        result = evaluate_compliance(
            {'resourceType': 'notEC2'},
            'i-11',
            'a',
            'b'
        )
        self.assertEqual(result, 'NOT_APPLICABLE')

    def test_is_compliant(self):
        result = evaluate_compliance(
            {'resourceType': 'AWS::EC2::Instance'},
            self.instance_id,
            'InstanceType',
            't2.small'
        )
        self.assertEqual(result, 'COMPLIANT')

    def test_is_non_compliant(self):
        result = evaluate_compliance(
            {'resourceType': 'AWS::EC2::Instance'},
            self.instance_id,
            'InstanceType',
            'm3.medium'
        )
        self.assertEqual(result, 'NON_COMPLIANT')

    def test_attribute_not_found(self):
        result = evaluate_compliance(
            {'resourceType': 'AWS::EC2::Instance'},
            self.instance_id,
            'FakeKey',
            'FakeValue'
        )
        self.assertEqual(result, 'NON_COMPLIANT')

    def test_json_attribute_value(self):
        result = evaluate_compliance(
            {'resourceType': 'AWS::EC2::Instance'},
            self.instance_id,
            'Monitoring',
            # Moto always returns monitoring disabled
            # when describing an instance
            {'State': 'disabled'}
        )
        self.assertEqual(result, 'COMPLIANT')


if __name__ == '__main__':
    unittest.main()
