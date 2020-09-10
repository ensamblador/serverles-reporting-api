#!/usr/bin/env python3

from aws_cdk import core

from ondemand_reports.ondemand_reports_stack import OndemandReportsStack


app = core.App()
OndemandReportsStack(app, "ondemand-reports")

app.synth()
