#!/usr/bin/env python3

import os
import aws_cdk as cdk
from aws_cdk import aws_iam as iam, aws_cloudformation as cloudformation


class GitHubRoleStack(cdk.Stack):
    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stack_vars = self.node.try_get_context("stacks")[cdk.Stack.of(self).stack_name]

        github_provider = iam.OpenIdConnectProvider(
            self,
            "GitHubProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
            thumbprints=["6938fd4d98bab03faadb97b34396831e3780aea1"],
        )

        roles = stack_vars["roles"]

        for role in roles:
            role_name = role["role_name"]
            github_org = role["github_org"]
            github_repo = role["github_repo"]

            github_role = iam.Role(
                self,
                role_name,
                role_name=role_name,
                assumed_by=iam.OpenIdConnectPrincipal(github_provider).with_conditions(
                    {
                        "StringEquals": {
                            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                        },
                        "StringLike": {
                            "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:*"
                        },
                    }
                ),
            )

            github_policy = iam.Policy(
                self,
                f"{role_name}Policy",
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["sts:AssumeRole"],
                        resources=[
                            "arn:aws:iam::*:role/cdk-*-deploy-role-*",
                            "arn:aws:iam::*:role/cdk-*-lookup-role-*",
                            "arn:aws:iam::*:role/cdk-*-file-publishing-role-*",
                        ],
                    ),
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["cloudformation:*"],
                        resources=["*"],
                    ),
                ],
            )

            github_role.attach_inline_policy(github_policy)

            cdk.CfnOutput(self, f"{role_name}Output", value=github_role.role_arn)


app = cdk.App()

syd_env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region="ap-southeast-2"
)

GitHubRoleStack(app, "github-roles", env=syd_env)

app.synth()
