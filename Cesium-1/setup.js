// Set center to be the geographic center of the United States
var extent = Cesium.Rectangle.fromDegrees(-100,25,-95,55);
Cesium.Camera.DEFAULT_VIEW_RECTANGLE = extent;
Cesium.Camera.DEFAULT_VIEW_FACTOR = 0;
function LabelCollectionGeocoder() {}
var viewer = new Cesium.Viewer('cesiumContainer', {
  timeline : false,
  animation : false,
  baseLayerPicker : false,
  sceneModePicker : false,
  creditContainer : "hideCredits",
  geocoder: new LabelCollectionGeocoder()
});

// Limit the user's ability to zoom out
viewer.scene.screenSpaceCameraController.maximumZoomDistance=15000000;
// Limit the user's ability to zoom in
viewer.scene.screenSpaceCameraController.minimumZoomDistance=1000;
