
# awscache

This `awscache` utility makes it easy to view the role sessions your use of the `aws` ([awscli](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html)) command has cached in `~/.aws/cli/cache/`. Every time you access an MFA-protected role the `aws` command caches the created session for the length of the validity period (usually 6-8h). During this time you won't be re-prompted for the MFA token for the same role because of the caching.

For example, assuming a configuration like this:

```
# ~/.aws/config:

[default]
region=us-east-1
output=json

[profile my-iam-profile] 
mfa_serial=arn:aws:iam::123456789000:mfa/vwalveranta
region=us-east-2

[profile some-role-requiring-mfa]
role_arn=arn:aws:iam::123456789999:role/developer-role
source_profile=my-iam-profile
role_session_name=vwalveranta
mfa_serial=arn:aws:iam::123456789000:mfa/vwalveranta
region=us-east-1


# ~/.aws/credentials:

[my-iam-profile]
aws_access_key_id = AKIAXXXXXXXXXXXXXXXX
aws_secret_access_key = SECRETsecretSECRETsecretSECRETsecretSECR
```

Any time you execute a command like:

```
aws --profile some-role-requiring-mfa s3 ls
```

The `aws` command first checks whether there is a corresponding cached role session present at `~/.aws/cli/cache/`. If not, you're prompted for your TOTP token and a cache file is created. 

To get started with `awscache` install the Python requirements to your environment by executing `pip install -r requirements.txt`

After that, you can simply execute: `python awscache.py` to get a listing of the cached role sessions and the length of time each session is still valid. You have the options to export a session's credentials for bash environment or for inclusion in an SQL query. You can also invalidate a specific session or all cached sessions so that you'll be prompted for the TOTP token on the next access of the role. The session validity timer is also reset whenever the TOTP token is entered. The script also checks each session file on every execution and purges any expired session files.

Note that at least Python 3.7 is required for this utility to run correctly.

A small utility to clear any `AWS_` variables from the shell environment is also included. Just source `source-this-to-clear-AWS-envvars.sh` and it'll display any `AWS_` variables present in the shell environment and give you the option to clear them out, like so:

`source source-this-to-clear-AWS-envvars.sh`
