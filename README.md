# ChurchTools Livestream Automation

# Setup

Everything is configured inside the config file `ctla_config.json`, which can also be given via the `-c` / `--config`
command line option.

Below follows the setup required on each external platform so that the app can interact with them.

## ChurchTools

<!-- TODO -->

## YouTube

1. Enable YouTube APIs for your Google Cloud project as
   described [here](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps#enable-apis)
2. Create
   the [authorization credentials](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps#creatingcred)
   for your app
3. Save the `client_secrets.json` from Google into your workspace and point the path in Your configuration file to it.