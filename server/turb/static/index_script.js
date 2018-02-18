var map;
var overlay;

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.8283, lng: -98.5795},
    zoom: 4,
    mapTypeId: 'satellite'
  });
  var input = document.getElementById('pac-input');

  var autocomplete = new google.maps.places.Autocomplete(
      input, {placeIdOnly: true});
  autocomplete.bindTo('bounds', map);

  map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

  var infowindow = new google.maps.InfoWindow();
  var infowindowContent = document.getElementById('infowindow-content');
  infowindow.setContent(infowindowContent);
  var geocoder = new google.maps.Geocoder;
  var marker = new google.maps.Marker({
    map: map
  });
  marker.addListener('click', function() {
    infowindow.open(map, marker);
  });

  autocomplete.addListener('place_changed', function() {
    infowindow.close();
    var place = autocomplete.getPlace();

    if (!place.place_id) {
      return;
    }
    geocoder.geocode({'placeId': place.place_id}, function(results, status) {

      if (status !== 'OK') {
        window.alert('Geocoder failed due to: ' + status);
        return;
      }
      map.setZoom(11);
      map.setCenter(results[0].geometry.location);
      // Set the position of the marker using the place ID and location.
      marker.setPlace({
        placeId: place.place_id,
        location: results[0].geometry.location
      });
      marker.setVisible(true);
      infowindowContent.children['place-name'].textContent = place.name;
      infowindowContent.children['place-id'].textContent = place.place_id;
      infowindowContent.children['place-address'].textContent =
          results[0].formatted_address;
      infowindow.open(map, marker);
    });
  });

  heatmap = new google.maps.visualization.HeatmapLayer({
    data: getPoints(),
    map: map,
    radius: 15
  });


  USGSOverlay.prototype = new google.maps.OverlayView();

  USGSOverlay.prototype.onAdd = function() {
    var div = document.createElement('div');
    div.style.borderStyle = 'none';
    div.style.borderWidth = '0px';
    div.style.position = 'absolute';
    var img = document.createElement('img');
    img.src = this.image_;
    img.style.width = '100%';
    img.style.height = '100%';
    img.style.position = 'absolute';
    div.appendChild(img);
    this.div_ = div;
    var panes = this.getPanes();
    panes.overlayLayer.appendChild(div);
  };

  USGSOverlay.prototype.draw = function() {
    var overlayProjection = this.getProjection();
    var sw = overlayProjection.fromLatLngToDivPixel(this.bounds_.getSouthWest());
    var ne = overlayProjection.fromLatLngToDivPixel(this.bounds_.getNorthEast());
    var div = this.div_;
    div.style.left = sw.x + 'px';
    div.style.top = ne.y + 'px';
    div.style.width = (ne.x - sw.x) + 'px';
    div.style.height = (sw.y - ne.y) + 'px';
  };

  USGSOverlay.prototype.onRemove = function() {
    this.div_.parentNode.removeChild(this.div_);
    this.div_ = null;
  };

  // Set the visibility to 'hidden' or 'visible'.
  USGSOverlay.prototype.hide = function() {
    if (this.div_) {
      // The visibility property must be a string enclosed in quotes.
      this.div_.style.visibility = 'hidden';
    }
  };

  USGSOverlay.prototype.show = function() {
    if (this.div_) {
      this.div_.style.visibility = 'visible';
    }
  };

  USGSOverlay.prototype.toggle = function() {
    if (this.div_) {
      if (this.div_.style.visibility === 'hidden') {
        this.show();
      } else {
        this.hide();
      }
    }
  };

  USGSOverlay.prototype.toggleDOM = function() {
    if (this.getMap()) {
      this.setMap(null);
    } else {
      this.setMap(this.map_);
    }
  };

  var bounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(0, -15),
        new google.maps.LatLng(20, 15));
  var srcImage = 'https://developers.google.com/maps/documentation/' +
      'javascript/examples/full/images/talkeetna.png';
  srcImage = '/static/test.png'

  function USGSOverlay(bounds, image, map) {
    this.bounds_ = bounds;
    this.image_ = image;
    this.map_ = map;
    this.div_ = null;
    this.setMap(map);
  }

  overlay = new USGSOverlay(bounds, srcImage, map);
}

function toggleHeatmap() {
 heatmap.setMap(heatmap.getMap() ? null : map);
}

function initAutocomplete() {
  var map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: -33.8688, lng: 151.2195},
    zoom: 13,
    mapTypeId: 'roadmap'
  });

  // Create the search box and link it to the UI element.
  var input = document.getElementById('pac-input');
  var searchBox = new google.maps.places.SearchBox(input);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

  // Bias the SearchBox results towards current map's viewport.
  map.addListener('bounds_changed', function() {
    searchBox.setBounds(map.getBounds());
  });

  var markers = [];
  // Listen for the event fired when the user selects a prediction and retrieve
  // more details for that place.
  searchBox.addListener('places_changed', function() {
    var places = searchBox.getPlaces();

    if (places.length == 0) {
      return;
    }

    // Clear out the old markers.
    markers.forEach(function(marker) {
      marker.setMap(null);
    });
    markers = [];

    // For each place, get the icon, name and location.
    var bounds = new google.maps.LatLngBounds();
    places.forEach(function(place) {
      if (!place.geometry) {
        console.log("Returned place contains no geometry");
        return;
      }
      var icon = {
        url: place.icon,
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(17, 34),
        scaledSize: new google.maps.Size(25, 25)
      };

      // Create a marker for each place.
      markers.push(new google.maps.Marker({
        map: map,
        icon: icon,
        title: place.name,
        position: place.geometry.location
      }));

      if (place.geometry.viewport) {
        // Only geocodes have viewport.
        bounds.union(place.geometry.viewport);
      } else {
        bounds.extend(place.geometry.location);
      }
    });
    map.fitBounds(bounds);
  });
}
