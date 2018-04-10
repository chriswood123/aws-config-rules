provider "aws" {
    region = "eu-west-1"
}

provider "archive" {}

data "archive_file" "zip" {
    type        = "zip"
    source_file = "instance_attribute.py"
    output_path = "instance_attribute.zip"
}

variable "AttributeKey" {}
variable "AttributeValue" {}

data "aws_iam_policy_document" "lambda_assumerole_policy" {
    statement {
        actions     = [
            "sts:AssumeRole"
        ]
        principals  = {
            type        = "Service"
            identifiers = [ "lambda.amazonaws.com" ]
        }
    }
}

data "aws_iam_policy_document" "lambda_policy" {
    statement {
        sid         = "lambdaExecution"
        actions     = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]
        resources   = [ "arn:aws:logs:*:*:*" ]
    }
    statement {
        sid         = "configExecution"
        actions     = [
            "config:Put*",
            "config:Get*",
            "config:List*",
            "config:Describe*"
        ]
        resources   = [ "*" ]
    }
    statement {
        sid         = "ec2Describe"
        actions     = [ "ec2:Describe*" ]
        resources   = [ "*" ]
    }
}

resource "aws_iam_role" "lambda_role" {
    assume_role_policy = "${data.aws_iam_policy_document.lambda_assumerole_policy.json}"
}

resource "aws_iam_role_policy" "lambda_role_policy" {
    role    = "${aws_iam_role.lambda_role.id}"
    policy  = "${data.aws_iam_policy_document.lambda_policy.json}"
}

resource "aws_lambda_function" "lambda_function" {
    function_name       = "instance_attribite_config_check"
    filename            = "${data.archive_file.zip.output_path}"
    source_code_hash    = "${data.archive_file.zip.output_sha}"
    role                = "${aws_iam_role.lambda_role.arn}"
    handler             = "instance_attribute.lambda_handler"
    runtime             = "python3.6"
}

resource "aws_lambda_permission" "lambda_permission" {
    statement_id    = "instance_attribite_config_check_perms"
    action          = "lambda:InvokeFunction"
    function_name   = "${aws_lambda_function.lambda_function.function_name}"
    principal       = "config.amazonaws.com"
}

resource "aws_config_config_rule" "config_rule" {
    name                = "instance_attribute_check"
    input_parameters    = "{\"AttributeKey\": \"${var.AttributeKey}\", \"AttributeValue\": \"${var.AttributeValue}\"}"
    source {
        owner   = "CUSTOM_LAMBDA"
        source_detail {
            event_source = "aws.config"
            message_type = "ConfigurationItemChangeNotification"
        }
        source_identifier = "${aws_lambda_function.lambda_function.arn}"
    }
    scope {
        compliance_resource_types = [ "AWS::EC2::Instance" ]
    }
}