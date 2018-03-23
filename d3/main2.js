var width = 1000,
    height = 700,
    active = d3.select(null);

var projection = d3.geoAlbersUsa() // updated for d3 v4
    .scale(1000)
    .translate([width / 2, height / 2]);

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
d3.queue()
    .defer(d3.json, "us.json")
    .defer(d3.json, "airports.json")
    .defer(d3.json, "turbEx.json")
    .await(ready)

function ready(error, us, airports, turbEx) {
    if (error) throw error;

    g.selectAll("path")
        .data(topojson.feature(us, us.objects.states).features)
        .enter().append("path")
        .attr("d", path)
        .attr("class", "feature")
        .on("click", clicked);

    g.append("path")
        .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
        .attr("class", "mesh")
        .attr("d", path);


    g.append("path")
        .datum(topojson.feature(airports, airports.objects.airports))
        .attr("class", "points")
        .attr("d", path);

    console.log(turbEx)
    //another example of how to add data pts:
    aa = [-122.490402, 37.786453, 8];
    bb = [-102.389809, 37.72728,20];
    g.selectAll("circle")
        .data([aa,bb]).enter()
    //     .data.forEach(function(d){
    //         d.Source = d.Source;
    //         d.Lon = +d.Lon;
    //         d.Lat = +d.Lat;
    //         d.Mag = +d.Mag;
    //
    // }).enter()
        .append("circle")
        .attr("fill", "red")
    updateLayers()




};

function updateLayers() {
    g.selectAll('circle')
        .attr("cx", function (d) { return projection(d)[0].lon; })
        .attr("cy", function (d) { return projection(d)[1].lat; })
        .attr("r", function(d) {return d[2]+"px"})

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
