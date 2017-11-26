/**
 * This class is an example of a custom geocoder. It provides geocoding by searching inside a LabelCollection.
 * @alias LabelCollectionGeocoder
 * @constructor
 */

function LabelCollectionGeocoder() {
}

/**
 * The function called to geocode using this geocoder service.
 *
 * @param {String} input The query to be sent to the geocoder service
 * @returns {Promise<GeocoderResult[]>}
 */



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
                console.log(resultObject);
                var lonlat = Cesium.Ellipsoid.WGS84.cartesianToCartographic(resultObject.position);
                var heightmin = 10000;
                var heightmax = 10000;
                if (resultObject.distanceDisplayCondition.near) heightmin = resultObject.distanceDisplayCondition.near;
                if (resultObject.distanceDisplayCondition.far) heightmax = resultObject.distanceDisplayCondition.far;
                var horizdeg = Math.sqrt(.5*6371000*(heightmax+heightmin)/2)/111000;
                console.log(horizdeg);
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
                return returnObject;
            });
        });

};


var czml = [{
    "id" : "document",
    "name" : "CZML Point",
    "version" : "1.0"
}, {
    "id" : "point 0",
    "name": "point 0",
    "position" : {
        "cartographicDegrees" : [17.0, 44.8, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 1",
    "name": "point 1",
    "position" : {
        "cartographicDegrees" : [49.9, 56.7, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 2",
    "name": "point 2",
    "position" : {
        "cartographicDegrees" : [17.0, 25.4, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 3",
    "name": "point 3",
    "position" : {
        "cartographicDegrees" : [9.6, 33.3, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 4",
    "name": "point 4",
    "position" : {
        "cartographicDegrees" : [21.0, 1.9, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 5",
    "name": "point 5",
    "position" : {
        "cartographicDegrees" : [49.3, 25.8, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 6",
    "name": "point 6",
    "position" : {
        "cartographicDegrees" : [4.6, 26.6, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 7",
    "name": "point 7",
    "position" : {
        "cartographicDegrees" : [19.8, 2.0, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 8",
    "name": "point 8",
    "position" : {
        "cartographicDegrees" : [6.1, 44.2, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}, {
    "id" : "point 9",
    "name": "point 9",
    "position" : {
        "cartographicDegrees" : [50.6, 51.2, 0]
    },
    "point": {
        "color": {
            "rgba": [255, 255, 255, 255]
        },
        "outlineColor": {
            "rgba": [255, 0, 0, 255]
        },
        "outlineWidth" : 4,
        "pixelSize": 20
    }
}];


var viewer = new Cesium.Viewer('cesiumContainer', {
    geocoder: new LabelCollectionGeocoder()
});
viewer.dataSources.add(Cesium.CzmlDataSource.load(czml));

var tax_labels = viewer.scene.primitives.add(new Cesium.LabelCollection() );       
for (var i = 1; i < airports.length; i++) {
   tax_labels.add( {position : Cesium.Cartesian3.fromDegrees(czml[i].position.cartographicDegrees[0], czml[i].position.cartographicDegrees[1]), text : czml[i].name, font : '15.75px sans-serif', distanceDisplayCondition : new Cesium.DistanceDisplayCondition(10442450.000000,25000000.000000) });
}