from cartopandas import CartoDF
import json

cred = json.load(open('credentials.json'))

cdf = CartoDF(cred['username'], api_key=cred['api_key'])
eqs = cdf.get_table('all_month_3')
new_df = eqs[['time', 'latitude', 'longitude', 'mag', 'place']]

new_df['mag'] = 10**(new_df['mag'])
new_df.head()

cdf.to_carto(new_df, 'mehaks_favorite_dataframe')
