let table_parent = document.getElementById("table_parent");

let mapChart;
let compareBtn = document.getElementById("compare");
let crimeRateSingle= document.getElementById('crimeRateSingle');
let crimeRateMultiple= document.getElementById('crimeRateMultiple');
// document
//   .getElementById("nav-map-tab")
//   .addEventListener("shown.bs.tab", function () {
//     mapChart.map.resize();
//   });
let crimeRateSide = "single";
const DEFAULT_COMPARE_DROPDOWN_MESSAGE = "Nothing selected";
const pull = document.getElementById("pull");
const addressButton = document.getElementById("addressSearchButton");
const cityInput = document.getElementById("city");
const startInput = document.getElementById("start");
const endInput = document.getElementById("end");
// const cityCompareInput = document.getElementById("cityCompare");
const cityCompareInput = document.getElementsByClassName(
    "filter-option-inner-inner"
);

// Reset map's data when city is selected
// (Prevents specific address lookup button from triggering after city change) 
document.getElementById("city").addEventListener('change', function(){
    mapChart.resetCity();
})

function isValidInputs(city, start, end){
    if (isNaN(start) || city === 'Select City') {
        insert_error("City Selection or Start Year Missing");
        return false;
    }
    if (start < 2020 || start > 2021) {
        insert_error("Start Year Must Be Between 2020-2021");
        return false;   
    }
    if (!isNaN(end) && (end < 2020 || end > 2021 || start > end)) {
        insert_error("End Year Must Be Between 2020-2021");
        return false;
    }
    return true
}

function getOtherCities(){
    let cities = cityCompareInput[0].innerHTML;
    if(cities === DEFAULT_COMPARE_DROPDOWN_MESSAGE){
        return null
    }
    return cities
}
function generateGraphs() {
    let city = cityInput.value;
    let start = parseInt(startInput.value);
    let end = parseInt(endInput.value);

    // Returns null instead of the dropdown's default message (for comparison purposes w/ null)
    let otherCities = getOtherCities();
    
    // Validation
    if(!isValidInputs(city, start, end)){
        return
    }

    generateMap(city, start, end, otherCities);
    generatePieChart(city, start, end, otherCities);
    generateLineGraph(city, start, end, otherCities);
    generateBarGraph(city, start, end, otherCities);
    generateStackedBarGraph(city, start, end, otherCities);
    generateCrimeTables(city, start, end, otherCities)

    // let chartContainer = document.getElementById("chart-container");
    // chartContainer.classList.remove("hidden");
    mapChart.map.resize();
}

pull.addEventListener("click", generateGraphs);
addressButton.addEventListener("click", searchSpecificLocation)


function generateMap(city, start, end, otherCities) {
    // Don't get map data if there isn't an address, or if we are Comparing cities
    if (otherCities != null) {
        return;
    }

    let dropdownCity = city;
    let radius = mapChart.getRadius();

    // Get dropdown City's geolocation data
    const apiKey = "319cf01c353142f082ee1055a6689222";
    var url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(city)}&format=json&limit=5&apiKey=${apiKey}`;
    fetch(url)
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        let output = data.results[0]
        mapChart.setAddressData(output);
    }).then(_ => {
        // Now do the actual map updating
        let lat = mapChart.centerLat;
        let lon = mapChart.centerLon;
        fetch(
            `http://127.0.0.1:5000/crimes_from_address?dropdownCity=${dropdownCity}&cityName=${city}&start=${start}&end=${end}&radius=${radius}&lat=${lat}&lon=${lon}`
        )
            .then((response) => {
                return response.json();
            })
            .then((res) => {
                if (res.errors.length) {
                    insert_error(`Error: ${res.errors[0]}`);
                } else {
                    mapChart.sendData(res.features, res.center);
                    let crimeScoreBox = document.getElementById("safety-score-box");
                    crimeScoreBox.innerHTML = res.crimeScore;
                    let crimeScoreBoxLabel = document.getElementById("safety-score-label");
                    crimeScoreBoxLabel.innerHTML = res.crimeScoreLabel;
    
                    let crimeRateBox = document.getElementById("crime-rate-box");
                    crimeRateBox.innerHTML = res.crimeRate;
                    let crimeRateBoxLabel = document.getElementById("crime-rate-label");
                    crimeRateBoxLabel.innerHTML = res.crimeRateLabel;
                    // Resets map data
                    mapChart.resetCity()
                }

            });
    })
    



}


function searchSpecificLocation(){
    inputBox = document.getElementById("addressInputBox")
    let dropdownCity = cityInput.value;
    let start = parseInt(startInput.value);
    let end = parseInt(endInput.value);
    let radius = mapChart.getRadius();

    // Returns null instead of the dropdown's default message (for comparison purposes w/ null)
    let otherCities = getOtherCities();
    
    // Validation
    if(!isValidInputs(dropdownCity, start, end)){
        return
    }
    let city = mapChart.cityName;
    if(city == null || !inputBox.value || (inputBox.value == inputBox.placeholder)){
        insert_error(`Please type a valid address for ${dropdownCity} before searching`)
        return
    }
    let lat = mapChart.centerLat;
    let lon = mapChart.centerLon;
    fetch(
        `http://127.0.0.1:5000/crimes_from_address?dropdownCity=${dropdownCity}&cityName=${city}&start=${start}&end=${end}&radius=${radius}&lat=${lat}&lon=${lon}`
    )
        .then((response) => {
            return response.json();
        })
        .then((res) => {
            if (res.errors.length) {
                insert_error(`Error: ${res.errors[0]}`);
            } else {
                mapChart.sendData(res.features, res.center);
                let crimeScoreBox = document.getElementById("safety-score-box");
                crimeScoreBox.innerHTML = res.crimeScore;
                let crimeScoreBoxLabel = document.getElementById("safety-score-label");
                crimeScoreBoxLabel.innerHTML = res.crimeScoreLabel;

                // Resets map data
                mapChart.resetCity()
            }
        });

}
function generatePieChart(city, start, end, otherCities) {
    if (otherCities != null) {
        console.log("TEMPORARY: No Pie Chart gen. due to comparison");
        return; // TODO Replace pie chart with stacked bar chart
    } else {
        fetch(
            `http://127.0.0.1:5000/crimes_pie_chart?city=${city}&start=${start}&end=${end}`
        )
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                $(document).ready(function () {
                    // console.log(data.counts);
                    var pieChart_data = [
                        {
                            type: "pie",
                            title: "Crime Pie Chart",
                            values: data.property_counts,
                            labels: data.property_crimes,
                        },
                    ];
                    var layout = {
                        height: 600,
                        width: 600,
                    };
                    Plotly.newPlot("pieChart", pieChart_data, layout);
                });
            });
    }
}

function generateLineGraph(city, start, end, otherCities) {
    if (otherCities != null) {
        console.log("TEMPORARY: No Line Graph gen. due to comparison");
        return; // TODO Accomodate other cities on graph
    } else {
        fetch(
            `http://127.0.0.1:5000/crimes_line_graph?city=${city}&start=${start}&end=${end}`
        )
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                $(document).ready(function () {
                    var countsByYearMonth = {};
                    for (var i = 0; i < data.dates.length; i++) {
                        var splitDate = data.dates[i].split("/");
                        var year = parseInt(splitDate[1]);
                        if (!isNaN(year)) {
                            var month = splitDate[0];
                            if (!countsByYearMonth[year]) {
                                countsByYearMonth[year] = {};
                            }
                            if (!countsByYearMonth[year][month]) {
                                countsByYearMonth[year][month] = 0;
                            }
                            countsByYearMonth[year][month] += data.counts[i];
                        }
                    }

                    var lineGraph_data = [];
                    for (var year in countsByYearMonth) {
                        var x = [];
                        var y = [];
                        for (var month in countsByYearMonth[year]) {
                            x.push(getMonthName(parseInt(month)));
                            y.push(countsByYearMonth[year][month]);
                        }

                        var monthOrder = [
                            "Jan",
                            "Feb",
                            "Mar",
                            "Apr",
                            "May",
                            "Jun",
                            "Jul",
                            "Aug",
                            "Sep",
                            "Oct",
                            "Nov",
                            "Dec",
                        ];
                        x.sort((a, b) => monthOrder.indexOf(a) - monthOrder.indexOf(b));
                        y.sort(
                            (a, b) =>
                                monthOrder.indexOf(x[y.indexOf(a)]) -
                                monthOrder.indexOf(x[y.indexOf(b)])
                        );

                        lineGraph_data.push({
                            type: "scatter",
                            y: y,
                            x: x,
                            name: year.toString(),
                        });
                    }

                    var layout = {
                        title: "Crime Timeline",
                        xaxis: {
                            title: "Month",
                        },
                        yaxis: {
                            title: "Number of Crimes",
                            rangemode: "tozero",
                        },
                    };

                    Plotly.newPlot("lineGraph", lineGraph_data, layout);
                });
            });
    }
}

const crimeTypes = ["Property", "Person", "Society", "Other"];

const barModes = {
    Group: "group",
    Stack: "stack",
};

function getBarModeLayout(barmode, title, xAxisTitle, yAxisTitle) {
    let layout = {
        barmode: barmode,
        title: title,
        xaxis: {title: xAxisTitle},
        yaxis: {title: yAxisTitle},
        // paper_bgcolor: "black",
        // plot_bgcolor: "black",
    };
    return layout;
}

function generateBarGraph(city, start, end, otherCities) {
    // console.log(`bar other ${otherCities}`);
    if (otherCities != null) {
        let city2 = otherCities; // REPLACE with correct multi-city logic
        fetch(
            `http://127.0.0.1:5000/crimes_bar_graph?city=${city}&city2=${city2}&start=${start}&end=${end}`
        )
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                $(document).ready(function () {
                    var cityOne = {
                        type: "bar",
                        name: city,
                        y: data.counts,
                        x: data.crimes,
                    };
                    var cityTwo = {
                        type: "bar",
                        name: city2,
                        y: data.counts2,
                        x: data.crimes2,
                    };
                    var bar_data = [cityOne, cityTwo];
                    var layout = {
                        barmode: "group",
                        title: "Comparison of Crimes Committed",
                        xaxis: {title: "Categories by City"},
                        yaxis: {title: "Number of Crimes"},
                    };
                    Plotly.newPlot("barGraph", bar_data, layout);
                });
            });
    }
}

function getStackedBarTraces(xVals, yVals, name) {
    let trace = {
        x: xVals,
        y: yVals,
        name: name,
        type: "bar",
    };
    return trace;
}

function isString(s) {
    return isinstance(s, str);
}

function buildOtherCitiesList(otherCities) {
    let otherCitiesList = [];
    if (otherCities != null) {
        otherCities = otherCities.split(",");
        let i = 0;
        while (i < otherCities.length) {
            otherCities[i] = otherCities[i].trim();
            i += 1;
        }
        otherCitiesList.push(...otherCities);
    }
    return otherCitiesList;
}

function generateStackedBarGraph(city, start, end, otherCities) {
    let otherCitiesList = buildOtherCitiesList(otherCities);
    fetch(
        `http://127.0.0.1:5000/crimes_stacked_bar_graph?city=${city}&start=${start}&end=${end}&otherCities=${JSON.stringify(
            {other_cities: otherCitiesList}
        )}`
    )
        .then((response) => {
            return response.json();
        })
        .then((citiesInfo) => {
            let cityNames = Object.keys(citiesInfo);
            let crimeTypeCounts = {};

            for (let cityName of cityNames) {
                let cityInfo = citiesInfo[cityName];

                for (let crimeType in cityInfo) {
                    if (!crimeTypeCounts.hasOwnProperty(crimeType)) {
                        crimeTypeCounts[crimeType] = [];
                    }
                    crimeTypeCounts[crimeType].push(cityInfo[crimeType]);
                }
            }

            let data = [];
            for (let crimeType of crimeTypes) {
                let trace = getStackedBarTraces(
                    cityNames,
                    crimeTypeCounts[crimeType],
                    crimeType
                );
                data.push(trace);
            }

            let layout = getBarModeLayout(
                barModes.Stack,
                "Crimes by City and Crime Category",
                "City",
                "Number of Crimes"
            );

            Plotly.newPlot("stacked-bar-graph", data, layout);
        });
}

function getMonthName(monthNum) {
    var months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ];
    return months[monthNum - 1];
}

function generateCrimeTables(city, start, end, cities) {
    if (cities) {
        cities = JSON.stringify(cities);
    }
    fetch(`http://127.0.0.1:5000/crimes_rate_given_city?dropdownCity=${city}&cityName=${city}&start=${start}&end=${end}&cities=${cities}`)
        .then((response) => {
            return response.json();
        })
        .then((res) => {
            if ("crimeRate" in res) {
                let crimeRateBox = document.getElementById("crime-rate-box");
                crimeRateBox.innerHTML = res['crimeRate'];
                let crimeRateBoxLabel = document.getElementById("crime-rate-label");
                crimeRateBoxLabel.innerHTML = "per 1000 people";
                if(crimeRateSide==='multiple'){
                    $('#crimeRateMultiple').collapse('toggle');
                    $('#crimeRateSingle').collapse('toggle');
                    crimeRateSide='single';
                }
            } else if ('crimeRateMap' in res) {
                let crimeRateMap = res['crimeRateMap']
                let dataContainer = document.getElementById('dataTableContainer');
                dataContainer.innerHTML='';
                let newTable = document.createElement('table');
                newTable.setAttribute('id', 'table');
                dataContainer.appendChild(newTable);
                $("#table").bootstrapTable({
                    data: crimeRateMap,
                    // pageSize: 5,
                    // pageNumber: 1,
                    // pagination: true,
                    columns: [
                        {
                            field: 'cityName',
                            title: 'City Name',
                            sortable: true
                        },
                        {
                            field: 'crimeRate',
                            title: 'Crime Rate',
                            sortable: true
                        }
                    ]
                });
                newTable.classList.add('table-dark');
                if(crimeRateSide==='single'){
                    $('#crimeRateSingle').collapse('toggle');
                    $('#crimeRateMultiple').collapse('toggle');
                    crimeRateSide='multiple';
                }
            }
        })
}

// // pie graph
// pull.addEventListener("click", function () {
//     let city = document.getElementById("city").value
//     let start = document.getElementById("start").value
//     let end = document.getElementById("end").value
//     fetch(`http://127.0.0.1:5000/crimes_pie_chart?city=${city}&start=${start}&end=${end}`)
//         .then((response) => {
//             return response.json();
//         })
//         .then((data) => {
//             $(document).ready(function (){
//                 // console.log(data.counts);
//                 var pieChart_data = [{
//                     type: "pie",
//                     values: data.counts,
//                     labels: data.crimes
//                 }];
//                 var layout = {
//                     height: 800,
//                     width: 800
//                   };
//                 Plotly.newPlot('pieChart',pieChart_data, layout);
//             })
//         })
// })

// // line graph
// pull.addEventListener("click", function () {
//     let city = document.getElementById("city").value
//     let start = document.getElementById("start").value
//     let end = document.getElementById("end").value
//     fetch(`http://127.0.0.1:5000/crimes_line_graph?city=${city}&start=${start}&end=${end}`)
//         .then((response) => {
//             return response.json();
//         })
//         .then((data) => {
//             $(document).ready(function (){
//                 var countsByYearMonth = {}
//                 for (var i = 0; i < data.dates.length; i++) {
//                     var splitDate = data.dates[i].split("/")
//                     var year = parseInt(splitDate[1])
//                     if (!isNaN(year)) {
//                         var month = splitDate[0]
//                         if (!countsByYearMonth[year]) {
//                             countsByYearMonth[year] = {}
//                         }
//                         if (!countsByYearMonth[year][month]) {
//                             countsByYearMonth[year][month] = 0
//                         }
//                         countsByYearMonth[year][month] += data.counts[i]
//                     }
//                 }

//                 var lineGraph_data = []
//                 for (var year in countsByYearMonth) {
//                     var x = []
//                     var y = []
//                     for (var month in countsByYearMonth[year]) {
//                         x.push(getMonthName(parseInt(month)))
//                         y.push(countsByYearMonth[year][month])
//                     }

//                     var monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
//                     x.sort((a,b) => monthOrder.indexOf(a) - monthOrder.indexOf(b))
//                     y.sort((a,b) => monthOrder.indexOf(x[y.indexOf(a)]) - monthOrder.indexOf(x[y.indexOf(b)]))

//                     lineGraph_data.push({
//                         type: "scatter",
//                         y: y,
//                         x: x,
//                         name: year.toString()
//                     })
//                 }

//                 var layout = {
//                     title: 'Crime Timeline',
//                     xaxis: {
//                         title: 'Month'
//                     },
//                     yaxis: {
//                         title: 'Number of Crimes',
//                         rangemode: 'tozero'
//                     }
//                 };

//                 Plotly.newPlot('lineGraph', lineGraph_data, layout);

//             })
//         })
// })
// // bar graph
// pull.addEventListener("click", function () {
//     let city = document.getElementById("city").value
//     let start = document.getElementById("start").value
//     let end = document.getElementById("end").value
//     let city2 = document.getElementById("cityCompare").value

//     if (city2 != null) {
//         fetch(`http://127.0.0.1:5000/crimes_bar_graph?city=${city}&city2=${city2}&start=${start}&end=${end}`)
//         .then((response) => {
//             return response.json();
//         })
//         .then((data) => {
//             $(document).ready(function (){
//                 var cityOne = {
//                     type: "bar",
//                     name: city,
//                     y: data.counts,
//                     x: data.crimes
//                 };
//                 var cityTwo = {
//                     type: "bar",
//                     name: city2,
//                     y: data.counts2,
//                     x: data.crimes2
//                 };
//                 var bar_data = [cityOne, cityTwo];
//                 var layout = {
//                     barmode: 'group',
//                     title: 'Comparison of Crimes Committed',
//                     xaxis: { title: 'Categories by City' },
//                     yaxis: { title: 'Number of Crimes'}
//                 };
//                 Plotly.newPlot('barGraph', bar_data, layout);
//             })
//         })
//     }
// })

window.addEventListener("load", () => {
    // Initialize map
    $('#crimeRateSingle').collapse('toggle');
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

    mapChart = new MapChart("mapChart");
    let slider = document.getElementById("radRange");
    slider.onclick = function () {
        mapChart.setRadius(slider.value);
    };
});

