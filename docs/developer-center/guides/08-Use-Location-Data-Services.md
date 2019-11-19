## Use Location Data Services

In this guide we'll go through how to use Geocoding and Isolines services to find a good place for a bike rental store in the city of Madrid.

Data used:
- Web:
  - Bike rental stores addresses: https://www.esmadrid.com/en/bike-rental-in-madrid# 

- Madrid Data Portal:
  - Bikes and pedestrian capacity: https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=695cd64d6f9b9610VgnVCM1000001d4a900aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default
  - Bike station: https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=1239827b864f4410VgnVCM2000000c205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default
  - Resting Area for bikes: https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=ded03ff2568f4410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default

## Consuming Quota

- Check the quota and learn about the `dry_run` option to prevent consuming quota.

## Geocoding Service

We've a web with the addresses of bike rental stores, we can use this information to geocode them and place them in a map: https://www.esmadrid.com/en/bike-rental-in-madrid#

## Isolines Service

### Isodistances
- Calculate isodistances from other bike rental stores to visualize which places are not covered by other bike rental store (walking distance in metters)
- Add some points where we could open the bike rental store

### Isochrones
- Check wich areas are closer to bike stations and resting areas from the decided destinations

## Conclusion

- Show three possible locations for the bike rental store
