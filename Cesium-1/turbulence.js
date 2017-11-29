
var turbulenceOn = false;
var turbulenceLayer = null;
function toggleTurbulence() {
  if (!turbulenceOn) {
    if (turbulenceLayer === null) {
      turbulenceLayer = viewer.imageryLayers.addImageryProvider(new Cesium.SingleTileImageryProvider({
        url : 'Resources/Images/turbulence.png'
      }));
    } else {
      viewer.imageryLayers.add(turbulenceLayer)
    }
  } else {
    viewer.imageryLayers.remove(turbulenceLayer, false);
  }
  turbulenceOn = !turbulenceOn;
  checkbox.checked = turbulenceOn;
}

// Add turbulence button to toolbar
var arr = document.getElementsByClassName("cesium-viewer-toolbar");
if (arr.length > 0) {
  var toolbar = arr[0]
  var button = document.createElement("button");
  button.type = "button";
  button.onclick = toggleTurbulence;
  button.className = "cesium-button";
  var label = document.createElement("label");
  label.type = "label";
  label.style = "pointer-events: none;";
  var checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.style = "pointer-events: none;";
  label.appendChild(checkbox);
  label.appendChild(document.createTextNode("Turbulence"));
  button.appendChild(label);
  toolbar.appendChild(button);
}
