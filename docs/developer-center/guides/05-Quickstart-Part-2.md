## Quickstart Part 2

This is the second part of the [Quickstart Guide](/developers/cartoframes/guides/Quickstart-Part-1/), where you've learned how to import data and visualize it with CARTOframes. Now, let's share and publish your data.

To be able to do so, you have to log in to CARTO. You will need to create an API key and use the method `set_default_credentials` to create a session. If you haven't created an API key yet, check the [authentication reference](/developers/cartoframes/reference/#heading-Authentication) to learn how to get it.

Note: If you don't have an account yet, you can get a [free account](https://carto.com/help/getting-started/student-accounts/) if you are a student or [get a trial](https://carto.com/signup/) if you aren't.

```py
from cartoframes.auth import set_default_credentials

set_default_credentials(username='your_username', api_key='your_api_key')
```

### Publish and share your results

To finish your work, you want to share the results with some teammates. Also, it would be great if you could allow them to play with the information. Let's do that!

First, you have to upload the data used by your maps to CARTO using the `Dataset` class. We have two dataframes: the bikes sharing data (`bikeshare_df`) and the census track polygons (`census_track_df`)

```py
from cartoframes.data import Dataset

Dataset(bikeshare_df).upload(table_name='arlington_bikeshare', if_exists='replace')
Dataset(census_track_df).upload(table_name='arlington_census_track', if_exists='replace')
```

Now, let's add widgets so people are able to see some graphs about the information displayed and allow them to filter it. To do this, we only have to add `widget=True` to the helpers.

```py
final_map = Map([
    Layer('arlington_census_track'),
    size_continuous_layer('arlington_bikeshare', 'total_events', widget=True)
])

final_map
```

![Combine Layers with Widget](../../img/guides/quickstart/combine_layers_widget.png)

Cool! Now that you have a small dashboard to play with, let's publish it to CARTO so you are able to share it with anyone. To do this, you just need to call the [publish](/developers/cartoframes/examples/#example-publish-public-visualization) method from the `Map` class:

```py
final_map.publish('arlington_bikeshare_spots')
```

![Share output information](../../img/guides/quickstart/share_output.png)

Congratulations! You have finished this guide and have a sense about how CARTOframes can speed up your workflow. To continue learning, you can check the specific guides, check the [reference](/developers/cartoframes/reference/) to know everything about a class or a method or check the notebook [examples](/developers/cartoframes/examples/).
