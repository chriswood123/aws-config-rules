# Instance Attribute Config Rule

Allows any EC2 instance attribute to be used as an AWS Config rule, ensuring that instances have the specified value for a given attribute. These can be things such as virtualisation type or AMI.

## Running

This is intended to be run in the AWS Lambda environment, triggered by the AWS Config service.

### Rule Parameters

Two parameters are used: 'AttributeKey' and 'AttributeValue'. An example is below:

| Key            | Value        |
| -------------- | ------------ |
| AttributeKey   | InstanceType |
| AttributeValue | t2.micro     |

## Testing

Testing is done using unittest, e.g.

```
$ python3 test_instance_attribute.py
.....
----------------------------------------------------------------------
Ran 5 tests in 0.506s

OK
```

The tests use the moto library to mock the AWS EC2 service.

## Deployment

The [Cloudformation template](./instance_attribute_cfn.yaml) can be used to deploy the AWS Config rule and the Lambda function as a cloudformation stack.

A template [CLI input JSON file](./stack_params.json) can be modified to pass parameters when creating this stack. An example of the AWS CLI command to create a stack is shown below.

```
$ aws cloudformation create-stack \
  --stack-name ConfigInstanceAttributesStack \
  --cli-input-json file://stack_params.json \
  --template-body file://instance_attribute_cfn.yaml
```