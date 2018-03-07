var canvas = d3.select("canvas"),
    width = canvas.property("width"),
    height = canvas.property("height"),
    context = canvas.node().getContext("2d");

var projection = d3.geoOrthographic()
    .scale((height - 10) / 2)
    .translate([width / 2, height / 2])
    .precision(0.1);


var zoom = d3.zoom()
    .scaleExtent([1, 20])
    .on("zoom", zoomed);


var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
    //track where user clicked down
    .on("mousedown", function() {
        d3.event.preventDefault();
        //only if scale === 1
        if(s !== 1) return;
        initX = d3.mouse(this)[0];
        mouseClicked = true;
    })
    .on("mouseup", function() {
        if(s !== 1) return;
        rotated = rotated + ((d3.mouse(this)[0] - initX) * 360 / (s * width));
        mouseClicked = false;
    })
    .call(zoom);

function rotateMap(endX) {
    projection.rotate([rotated + (endX - initX) * 360 / (s * width),0,0])
    g.selectAll('path')       // re-project path data
        .attr('d', path);
}


var path = d3.geoPath()
    .projection(projection)
    .context(context);

canvas.call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged));

var render = function() {},
    v0, // Mouse position in Cartesian coordinates at start of drag gesture.
    r0, // Projection rotation as Euler angles at start.
    q0; // Projection rotation as versor at start.

function dragstarted() {
    v0 = versor.cartesian(projection.invert(d3.mouse(this)));
    r0 = projection.rotate();
    q0 = versor(r0);
}

function dragged() {
    var v1 = versor.cartesian(projection.rotate(r0).invert(d3.mouse(this))),
        q1 = versor.multiply(q0, versor.delta(v0, v1)),
        r1 = versor.rotation(q1);
    projection.rotate(r1);
    render();
}


// d3.json("https://gist.githubusercontent.com/tdreyno/4278655/raw/7b0762c09b519f40397e4c3e100b097d861f5588/airports.json", function(error, data) {
//
//
//     if (error) { return error; }
//
// });

d3.queue()
    //TODO: split combined.json so can have states hidden at specific zoom and ignore Canadian states
    .defer(d3.json, "combined.json")
    .defer(d3.json, "airports.json")
    .await(function(error, world, airports) {
        if (error) {
            console.error('Oh dear, something went wrong: ' + error);
        }
        else {
            var sphere = {type: "Sphere"},
                land = topojson.feature(world, world.objects.countries),
                usa =  topojson.feature(world, world.objects.states);
                //airport = topojson.feature(airports, airports);

            console.log(land);
            console.log(usa);
            console.log(airports);




            render = function() {
                context.clearRect(0, 0, width, height);
                context.beginPath(), path(sphere), context.fillStyle = "#f0f8ff", context.fill();
                context.beginPath(), path(land), context.fillStyle = "#f5fffa", context.fill(), context.stroke(), context.lineWidth = 0.35;
                context.beginPath(), path(usa), context.fillStyle = "#f5fffa", context.fill(), context.stroke(), context.lineWidth = 0.35;


                context.beginPath(), path(sphere), context.stroke();
            };

            render();
        }
    });

// d3.json("combined.json", function(error, world) {
//     d3.json("https://gist.githubusercontent.com/tdreyno/4278655/raw/7b0762c09b519f40397e4c3e100b097d861f5588/airports.json", function(error, airports) {
//         if (error) { return error; }
//     });
//
//     if (error) throw error;
//
//     var sphere = {type: "Sphere"},
//         land = topojson.feature(world, world.objects.countries),
//         usa =  topojson.feature(world, world.objects.states);
//
//     console.log(land);
//     console.log(usa);
//     console.log(airports);
//
//
//     render = function() {
//         context.clearRect(0, 0, width, height);
//         context.beginPath(), path(sphere), context.fillStyle = "#f0f8ff", context.fill();
//         context.beginPath(), path(land), context.fillStyle = "#f5fffa", context.fill(), context.stroke(), context.lineWidth = 0.35;
//         context.beginPath(), path(usa), context.fillStyle = "#f5fffa", context.fill(), context.stroke(), context.lineWidth = 0.35;
//
//
//         context.beginPath(), path(sphere), context.stroke();
//     };
//
//     render();
// });

function rotateMap(endX) {
    projection.rotate([rotated + (endX - initX) * 360 / (s * width),0,0])
    g.selectAll('path')       // re-project path data
        .attr('d', path);
}

function zoomed() {
    var t = d3.event.translate;
    s = d3.event.scale;
    var h = 0;
    t[0] = Math.min(
        (width/height)  * (s - 1),
        Math.max( width * (1 - s), t[0] )
    );
    t[1] = Math.min(
        h * (s - 1) + h * s,
        Math.max(height  * (1 - s) - h * s, t[1])
    );
    zoom.translate(t);
    if(s === 1 && mouseClicked) {
        rotateMap(d3.mouse(this)[0])
        return;
    }
    g.attr("transform", "translate(" + t + ")scale(" + s + ")");
    //adjust the stroke width based on zoom level
    d3.selectAll(".boundary")
        .style("stroke-width", 1 / s);

}