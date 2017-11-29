
LabelCollectionGeocoder.prototype.geocode = function (input) {
  viewer.entities.removeAll();
  var searchlist = [];

  for (var i = 0; i < airports.length; ++i) {
    var airport = airports[i];
      if (airport.lat != null && airport.lon != null && airport.name != null && airport.iso == "US" && (airport.name.toLowerCase().indexOf(input.toLowerCase()) > -1 || airport.iata.toLowerCase().indexOf(input.toLowerCase()) > -1)) {
          searchlist.push(airport);
      }
  }

  return Cesium.loadText("").then(function (results) {
    return searchlist.map(function (airport) {
      var position = Cesium.Cartesian3.fromDegrees(parseFloat(airport.lon), parseFloat(airport.lat));
      var lonlat = Cesium.Ellipsoid.WGS84.cartesianToCartographic(position);
      var heightmin = 10000;
      var heightmax = 20000;
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

      var geocoderResult =  {
          displayName: airport.name,
          destination: recto
      };

      viewer.entities.add({
          name: airport.name,
          position: position,
          point: {
            pixelSize: 5,
            color: Cesium.Color.RED,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2
          }
      })
      return geocoderResult;
    });
  });
};

/**
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
**/
