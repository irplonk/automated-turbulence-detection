
LabelCollectionGeocoder.prototype.geocode = function (input) {
  viewer.entities.removeAll();
  var searchlist = [];

  for (var i = 0; i < airport_labels.length; ++i) {
    var airport = airport_labels.get(i);
      if (airport.text.toLowerCase().indexOf(input.toLowerCase()) > -1) {
          searchlist.push(airport);
      }
  }

  return Cesium.loadText("").then(function (results) {
    return searchlist.map(function (resultObject) {
        var lonlat = Cesium.Ellipsoid.WGS84.cartesianToCartographic(resultObject.position);

        var heightmin = 10000;
        var heightmax = 10000;

        if (resultObject.distanceDisplayCondition.near) heightmin = resultObject.distanceDisplayCondition.near;
        if (resultObject.distanceDisplayCondition.far) heightmax = resultObject.distanceDisplayCondition.far;
        var horizdeg = Math.sqrt(.5*6371000*(heightmax+heightmin)/2)/111000;
        var nwlat = lonlat.latitude + Math.PI/180*horizdeg/2; if (nwlat > Math.PI/2) nwlat=(nwlat/Math.PI/2) % 1 * Math.PI/2;
        var nwlon = lonlat.longitude + Math.PI/360*horizdeg; if (nwlon > Math.PI) nwlon=(nwlon/Math.PI - 1) % 1 * Math.PI;
        var swlat = lonlat.latitude - Math.PI/180*horizdeg/2; if (swlat < -Math.PI/2) swlat=(swlat/Math.PI/2) % 1 * Math.PI/2;
        var swlon = lonlat.longitude - Math.PI/360*horizdeg; if (swlon < -Math.PI) swlon=(swlon/Math.PI + 1) % 1 * Math.PI;
        var carto = [
          new Cesium.Cartographic(swlon, swlat, heightmin),
          new Cesium.Cartographic(nwlon, nwlat, heightmax)
        ];
        var recto = Cesium.Rectangle.fromCartographicArray(carto);

        var returnObject =  {
            displayName: resultObject.text,
            destination: recto
        };

        var searchResult = findObjectByKey(airports, "name", returnObject.displayName);

        viewer.entities.add({
            name: searchResult.name,
            position: Cesium.Cartesian3.fromDegrees(parseFloat(searchResult.lon), parseFloat(searchResult.lat)),
            point: {
              pixelSize: 5,
              color: Cesium.Color.RED,
              outlineColor: Cesium.Color.WHITE,
              outlineWidth: 2
            }
        })
        return returnObject;
    });
  });
};

function findObjectByKey(array, key, value) {
  for (var i = 0; i < array.length; i++) {
      if (array[i][key] === value) {
          return array[i];
      }
  }
  return null;
}

viewer.dataSources.add(Cesium.CzmlDataSource.load(airports));

var airport_labels = viewer.scene.primitives.add(new Cesium.LabelCollection());

for (var i = 1; i < airports.length; i++) {
  if((airports[i].lat != null) && (airports[i].lon != null) && (airports[i].name != null) && (airports[i].iso == "US")) {
      airport_labels.add({
      position : Cesium.Cartesian3.fromDegrees(parseFloat(airports[i].lon), parseFloat(airports[i].lat)),
      text : airports[i].name,
      font : '15.75px sans-serif',
      distanceDisplayCondition : new Cesium.DistanceDisplayCondition(10000,20000)
    });
  }
}
