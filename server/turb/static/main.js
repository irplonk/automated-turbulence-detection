var width = 1000,
    height = 700,
    active = d3.select(null);

var projection = d3.geoMercator() // updated for d3 v4
    .scale((width - 3) / (2 * Math.PI))
    .translate([width / 2, height / 2]);
    //.scale(1000)
    //.translate([width / 2, height / 2]);

var zoom = d3.zoom()
// no longer in d3 v4 - zoom initialises with zoomIdentity, so it's already at origin
// .translate([0, 0])
// .scale(1)
    .scaleExtent([1, 8])
    .on("zoom", zoomed);

var path = d3.geoPath() // updated for d3 v4
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
    .on("click", stopped, true);

svg.append("rect")
    .attr("class", "background")
    .attr("width", width)
    .attr("height", height)
    .on("click", reset);

var g = svg.append("g");

svg
    .call(zoom); // delete this line to disable free zooming
// .call(zoom.event); // not in d3 v4

function ready(error, us, airports) {
    if (error) throw error;

    console.log(topojson.feature(us, us.features))

    g.selectAll("path")
        .data(us.features)
        .enter().append("path")
        .attr("d", path)
        .attr("class", "feature")
        .on("click", clicked);

    g.append("path")
        .datum(topojson.mesh(us, us.features, function(a, b) { return a !== b; }))
        .attr("class", "mesh")
        .attr("d", path);

    // Uncomment to see all of the airports
    // g.append("path")
    //     .datum(topojson.feature(airports, airports.objects.airports))
    //     .attr("class", "points")
    //     .attr("d", path);

    // Make call to retrieve turbulence data
    makeQuery(5, 1, 'reports', makeTurbulence);
}

/**
 * Makes call to retrieve information from server
 * @param max the maximum number of rows of information to receive back
 * @param start the starting index of information
 * @param table the type of table from which to retrieve information
 * @param callback the function to call with the response results
 */
function makeQuery(max, start, table, callback) {
    var xhttp = new XMLHttpRequest();
    var url = "http://127.0.0.1:8000/query";
    var params = "?max=" + max + "&start=" + start + "&table=" + table;
    url = url + params;
    xhttp.onreadystatechange = processRequest;
    function processRequest() {
        if (xhttp.readyState === 4 && xhttp.status === 200) {
            var response = JSON.parse(xhttp.response);
            callback(response.entries);
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

/**
 * Adds turbulence information to the map
 * @param reports the reports to be added
 */
function makeTurbulence(reports) {
    g.selectAll("circle")
        .data(reports).enter()
        .append("circle")
        .attr("fill", function (d) { return ((d.tke < 0.1) ? "green" : ( (d.tke < 0.3) ? "yellow" : "red")); })
        .attr("cx", function (d) { return projection([d.longitude, d.latitude])[0]; })
        .attr("cy", function (d) { return projection([d.longitude, d.latitude])[1]; })
        .attr("r", 8)
        .attr("opacity", 1.0)
}

function clicked(d) {
    if (active.node() === this) return reset();
    active.classed("active", false);
    active = d3.select(this).classed("active", true);

    var bounds = path.bounds(d),
        dx = bounds[1][0] - bounds[0][0],
        dy = bounds[1][1] - bounds[0][1],
        x = (bounds[0][0] + bounds[1][0]) / 2,
        y = (bounds[0][1] + bounds[1][1]) / 2,
        scale = Math.max(1, Math.min(8, 0.9 / Math.max(dx / width, dy / height))),
        translate = [width / 2 - scale * x, height / 2 - scale * y];

    svg.transition()
        .duration(750)
        // .call(zoom.translate(translate).scale(scale).event); // not in d3 v4
        .call( zoom.transform, d3.zoomIdentity.translate(translate[0],translate[1]).scale(scale) ); // updated for d3 v4
}

function reset() {
    active.classed("active", false);
    active = d3.select(null);

    svg.transition()
        .duration(750)
        // .call( zoom.transform, d3.zoomIdentity.translate(0, 0).scale(1) ); // not in d3 v4
        .call( zoom.transform, d3.zoomIdentity ); // updated for d3 v4
}

function zoomed() {
    g.style("stroke-width", 1.5 / d3.event.transform.k + "px");
    // g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")"); // not in d3 v4
    g.attr("transform", d3.event.transform); // updated for d3 v4
}

// If the drag behavior prevents the default click,
// also stop propagation so we don’t click-to-zoom.
function stopped() {
    if (d3.event.defaultPrevented) d3.event.stopPropagation();
}
