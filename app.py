#!/usr/bin/env python3

from aws_cdk import core

from ondemand_reports.ondemand_reports_stack import OndemandReportsStack


app = core.App()

OndemandReportsStack(app, "ondemand-reports", env={'region': 'us-west-1'},
                     athena_bucket_arn='arn:aws:s3:::athena-queries-us-west-1')

app.synth()
