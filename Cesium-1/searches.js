
var searchedLocation ="";

var searchArr = [];
var tempArr = [];

console.log(searchedLocation);
var searchResult;

LabelCollectionGeocoder.prototype.geocode = function (input) {

  var searchtext = input;
  var searchlist = [];

  var gcLC = tax_labels;
  var len = gcLC.length;
  for (var i = 0; i < len; ++i) {
    var l = gcLC.get(i);
      if ( l.text.toLowerCase().indexOf( searchtext.toLowerCase() ) > -1 ) {
          searchlist.push(l);
      }
  }

  return Cesium.loadText("")
      .then(function (results) {
          var bboxDegrees;
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
             console.log(carto);


              var recto = Cesium.Rectangle.fromCartographicArray(carto);
              var returnObject =  {
                  displayName: resultObject.text,
                  destination: recto
              };

              console.log(recto);


              searchedLocation = returnObject.displayName;


              searchResult = searchForPlace(searchedLocation);


              console.log(searchResult);
              tempArr[0] = searchResult;

              console.log(tempArr);

              viewer.entities.removeAll();

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
          console.log(returnObject);


      });


};


      console.log(searchResult);

function findObjectByKey(array, key, value) {
  for (var i = 0; i < array.length; i++) {
      if (ariports[i][key] === value) {
          return array[i];
      }
  }
  return null;
}


var tax_labels = viewer.scene.primitives.add(new Cesium.LabelCollection() );


function searchForPlace (searchedLocation) {
var searchResult = null;
  for (var i = 0; i < airports.length; i++) {
    if(airports[i].name == searchedLocation) {
      var searchResult = airports[i];
      return searchResult;
    }

}
return searchResult;
}


viewer.dataSources.add(Cesium.CzmlDataSource.load(airports));

var tax_labels = viewer.scene.primitives.add(new Cesium.LabelCollection() );

for (var i = 1; i < airports.length; i++) {
if((airports[i].lat != null) && (airports[i].lon != null) && (airports[i].name != null) && (airports[i].iso == "US") ) {
 tax_labels.add( {position : Cesium.Cartesian3.fromDegrees(parseFloat(airports[i].lon), parseFloat(airports[i].lat)),
  text : airports[i].name,
  font : '15.75px sans-serif',
  distanceDisplayCondition : new Cesium.DistanceDisplayCondition(10000,20000)
  });
}
}
