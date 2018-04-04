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

Testing is done using pytest, e.g.

```
$ pip3 install -r test-requirements.txt
$ pytest
============================================ test session starts =============================================
platform darwin -- Python 3.6.4, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
rootdir: /chriswood-config/instance_attribute, inifile:
collected 5 items

test_instance_attribute.py .....                                                                       [100%]

========================================== 5 passed in 1.71 seconds ==========================================
```

The tests use the moto library to mock the AWS EC2 service. 