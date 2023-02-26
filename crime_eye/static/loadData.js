let table_parent = document.getElementById("table_parent")
let graph = document.getElementById("graph")
let pull = document.getElementById("pull")
let mapTab = document.getElementById("nav-graph-tab")
let dataChanged = false
let geoData = {"type": "FeatureCollection", "features": []};
let mapChart; 

mapTab.addEventListener('shown.bs.tab', function () {
    map.resize()
})

// Should probably be separated into its own class 
// [Will prob be removed/revised anyway]
mapboxgl.accessToken = 'pk.eyJ1Ijoic3JhODQiLCJhIjoiY2w4ZjNmcXk4MDllbDQwbnpoOXJwa2VsZSJ9.OsLldCR-T9CjYaBE5Fa4OA';
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v11',
    center: [-97.62831376, 30.28096067],
    zoom: 11
});
map.on('load', () => {
    map.addSource('crime', {
        'type': 'geojson',
        'data': geoData
    });

    map.addLayer(
        {
            'id': 'crime-heat',
            'type': 'heatmap',
            'source': 'crime',
            'paint': {
                'heatmap-intensity': {
                    'stops': [
                        [11, 1],
                        [15, 3]
                    ]
                },
                'heatmap-color': [
                    'interpolate',
                    ['linear'],
                    ['heatmap-density'],
                    0,
                    'rgba(236,222,239,0)',
                    0.2,
                    'rgb(208,209,230)',
                    0.4,
                    'rgb(166,189,219)',
                    0.6,
                    'rgb(103,169,207)',
                    0.8,
                    'rgb(28,144,153)'
                ],
                'heatmap-radius': {
                    'stops': [
                        [11, 15],
                        [15, 20]
                    ]
                },
                'heatmap-opacity': {
                    'default': 1,
                    'stops': [
                        [14, 1],
                        [15, 0]
                    ]
                }
            }
        },
        'waterway-label'
    );
    setInterval(function () {
        if (dataChanged) {
            dataChanged = false
            let city = document.getElementById("city").value
            let start = document.getElementById("start").value
            let end = document.getElementById("end").value
            fetch(`http://127.0.0.1:5000/city_geo_json?city=${city}&start=${start}&end=${end}`)
                .then((response) => {
                    return response.json();
                })
                .then((data) => {
                    $(document).ready(function () {
                        map.getSource('crime').setData(data);
                        map.flyTo({
                            center: data["features"][0]["geometry"]["coordinates"],
                            essential: true
                        });
                    });
                });
        }
    }, 50);
});

function createTable() {
    let table = document.createElement("table");
    table.id = "table";
    let header = document.createElement("thead");
    let row = document.createElement("tr");

    let city = document.createElement("th");
    city.setAttribute("data-field", "CITY_NAME");
    city.innerText = "City"

    let state = document.createElement("th");
    state.setAttribute("data-field", "STATE_NAME");
    state.innerText = "State"

    let code = document.createElement("th");
    code.setAttribute("data-field", "CRIME_CODE");
    code.innerText = "Crime Code"

    let description = document.createElement("th");
    description.setAttribute("data-field", "CRIME_DESCRIPTION");
    description.innerText = "Description"

    let dateReported = document.createElement("th");
    dateReported.setAttribute("data-field", "DATE_REPORTED");
    dateReported.innerText = "Date Reported"

    let dateOccurred = document.createElement("th");
    dateOccurred.setAttribute("data-field", "DATE_OCCURRED");
    dateOccurred.innerText = "Date Occurred"

    let latitude = document.createElement("th");
    latitude.setAttribute("data-field", "LATITUDE");
    latitude.innerText = "Latitude"

    let longitude = document.createElement("th");
    longitude.setAttribute("data-field", "LONGITUDE");
    longitude.innerText = "Longitude"

    table.append(header)
    header.append(row)
    row.append(city)
    row.append(state)
    row.append(code)
    row.append(description)
    row.append(dateReported)
    row.append(dateOccurred)
    row.append(latitude)
    row.append(longitude)
    return table
}

pull.addEventListener("click", function () {
    let city = document.getElementById("city").value
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    fetch(`http://127.0.0.1:5000/city_crime_data?city=${city}&start=${start}&end=${end}`)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            $(document).ready(function () {
                while (table_parent.firstChild) {
                    table_parent.removeChild(table_parent.firstChild);
                }
                let tableElement = createTable();
                table_parent.append(tableElement);

                let table = document.getElementById("table");
                $('table').bootstrapTable({data: data.slice(0, 51)});

                dataChanged = true // Trigger for heatmap
            });
        });
});

// For radius chart 
pull.addEventListener("click", function () {
    let city = document.getElementById("city").value
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    let radius = mapChart.getRadius();
    fetch(`http://127.0.0.1:5000/crimes_in_radius?city=${city}&start=${start}&end=${end}&radius=${radius}`)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            $(document).ready(function () {
                // let cityCenter = [-71.0589, 42.3601] // TODO Get based on user input
                mapChart.sendData(data.coords, data.center); // TODO Change to more 
            });
        });
});

window.addEventListener("load", ()=>{
    // Initialize map
    mapChart = new MapChart("mapChart");


})