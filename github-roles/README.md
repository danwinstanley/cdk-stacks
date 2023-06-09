# GitHub Actions OIDC Roles

Simple stack that sets up a GitHub Actions OIDC in your AWS account and creates you per-org and per-repo roles for use with the `aws-actions/configure-aws-credentials` action.

See `cdk.json` for role configuration. You can add multiple roles by adding another dictionary to the list of `roles`.

Currently this only allows for assuming the default CDK bootstrapped roles, which may be too permissive for your use-case, so proceed with caution.
