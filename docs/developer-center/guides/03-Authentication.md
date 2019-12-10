## Authentication

### Introduction
This guide focuses on the basics of authentication in CARTOframes.

> To visualize your local data with CARTOframes, you don't need to be authenticated.

Authentication is needed to set up your credentials to save your data and visualizations to CARTO, to use [Location Data Services](/developers/cartoframes/guides/Location-Data-Services/), or the [Data Observatory](developers/cartoframes/guides/Data-discovery/). Since a CARTO account is required for these cases, if you don't already have an account, you can [create one here](https://carto.com/signup/).

### Get your Master API Key
Once you have created an account, you need to get your **Master** API Key. The API keys page can be accessed from your [CARTO Dashboard](https://carto.com/help/tutorials/your-dashboard-overview/). Once there, click on your avatar to open the dashboard menu. The API keys link will be shown.

![API Keys link - CARTO Dashboard](../../img/guides/credentials/dashboard.png)

From here, copy the **Master** API Key to use in the next section.

![Master API Key - CARTO Dashboard](../../img/guides/credentials/api-keys.png)

### Setting default credentials

With [set_default_credentials](/developers/cartoframes/reference/#cartoframes-auth-set_default_credentials), the same user's authentication will be used by every CARTOframes component. There are different ways to set them but we encourage you to use the one that reads the credentials from a JSON file:

```py
from cartoframes.auth import set_default_credentials

set_default_credentials('creds.json')
```

Example `creds.json` file:

```json
{
  "username": "YOUR_USERNAME",
  "api_key": "YOUR_API_KEY"
}
```

### Credential parameters

- `username`: your CARTO account username
- `api_key`: API Key of user's CARTO account. If the data to be accessed is **public**, it can be set to `default_public`.
- `base_url`: only needed for on-premise or custom installations. Typically in the form of `https://username.carto.com/` for user `username`. On-premises installation (and others) have a different URL pattern.

### Conclusion
In this guide you learned how to authenticate to CARTO reading your credentials from a file. [Check the reference](/developers/cartoframes/reference/#heading-Auth) to learn more about credentials and how to manage them.