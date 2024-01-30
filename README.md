# [Cryptomus](https://cryptomus.com) gateway module for [Fleio](https://fleio.com)

## Introduce

This module was developed by the [Fotbo](https://fotbo.com) team and is designed for integrating the Cryptomus payment method into Fleio.

- Cryptomus - Crypto Payment Gateway.
- The Fleio OpenStack Edition - billing system and self-service portal software - enables service providers to sell public cloud services.

## Getting started

First, it is necessary to clone the project and integrate the module into Fleio. For the integration, we will be using a custom Dockerfile.

1. Clone project .
```
git clone git@github.com:fotbo/cryptomus-gateway-module.git
```
2.  Now you need to added costume code into docker. For example, you can achieve this as follows:

```dockerfile
# define the build arguments that are used below to reference the base Docker backend image
ARG FLEIO_DOCKER_HUB
ARG FLEIO_RELEASE_SUFFIX

FROM ${FLEIO_DOCKER_HUB}/fleio_backend${FLEIO_RELEASE_SUFFIX}


ENV INSTALED_PATH="/var/webapps/fleio/project/fleio"

COPY --chown=fleio:fleio cryptomus-gateway-module $INSTALED_PATH/billing/gateways/cryptomus
```

More information at the [link](https://fleio.com/docs/2024.01/developer/add-change-docker-files.html)

3. After this, you need to add configurations in the `settings.py` file.
```
fleio edit settings.py
```

4. And put settings ([getting api keys](https://doc.cryptomus.com/getting-started/getting-api-keys)).
```
# >>> Cryptomus 

INSTALLED_APPS += ('fleio.billing.gateways.cryptomus', )

CRYPTOMUS_SETTINGS = {
    'merchant_id': 'secret',
    'api_key': 'secret',
    'url_success': '',
    'subtract': 100,
    'url_callback': '',
    'api_url': 'https://api.cryptomus.com/',
}
```

Save and restart fleio.
After restarting, you will have the option to enable the module for users in the graphical interface.