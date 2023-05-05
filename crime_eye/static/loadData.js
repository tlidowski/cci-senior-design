let table_parent = document.getElementById("table_parent");
const pull = document.getElementById("pull");
let mapChart;
let cityDropdown = document.getElementById("city-dropdown");

document
  .getElementById("nav-map-tab")
  .addEventListener("shown.bs.tab", function () {
    mapChart.map.resize();
  });

const cityInput = document.getElementById("city");
const startInput = document.getElementById("start");
const endInput = document.getElementById("end");
const cityCompareInput = document.getElementById("cityCompare");

function generateGraphs() {
  let city = cityInput.value;
  let start = startInput.value;
  let end = endInput.value;
  let otherCities = cityCompareInput.value;

  // TODO Do input validation here

  if (!start || !end ||!city){
    insert_error("Need all parameters please");
    return;
  }

  // TEMPORARY LOGIC
  if (otherCities == "Select") {
    otherCities = null;
  }
  generateMap(city, start, end, otherCities);
  generatePieChart(city, start, end, otherCities);
  generateLineGraph(city, start, end, otherCities);
  generateBarGraph(city, start, end, otherCities);

  //temporary
  let cityCompareInput2 = document.getElementById("cityCompare2");
  let otherCities2 = cityCompareInput2.value;
  //
  generateStackedBarGraph(city, start, end, otherCities2);

  // Reset Map Address
  mapChart.cityName = null;
}

pull.addEventListener("click", generateGraphs);

function generateMap(city, start, end, otherCities) {
  let cityName = mapChart.cityName;
  // Don't get map data if there isn't an address, or if we are Comparing cities
  if (cityName == null || otherCities != null) {
    return;
  }
  let lat = mapChart.centerLat;
  let lon = mapChart.centerLon;

  let dropdownCity = city;
  let radius = mapChart.getRadius();

  // Assuming validation on server
  fetch(
    `http://127.0.0.1:5000/crimes_from_address?dropdownCity=${dropdownCity}&cityName=${cityName}&start=${start}&end=${end}&radius=${radius}&lat=${lat}&lon=${lon}`
  )
    .then((response) => {
      return response.json(); // TODO should be replaced by validation before function call
    })
    .then((res) => {
      if (res.errors.length) {
        console.log(`Error: ${res.errors[0]}`);
      } else {
        mapChart.sendData(res.features, res.center);
        let crimeScoreBox = document.getElementById("crime-score-box");
        crimeScoreBox.innerHTML = res.crimeScore;
        let crimeScoreBoxLabel = document.getElementById("crime-score-label");
        crimeScoreBoxLabel.innerHTML = res.crimeScoreLabel;

        let crimeRateBox = document.getElementById("crime-rate-box");
        crimeRateBox.innerHTML = res.crimeRate;
        let crimeRateBoxLabel = document.getElementById("crime-rate-label");
        crimeRateBoxLabel.innerHTML = res.crimeRateLabel;
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
              values: data.counts,
              labels: data.crimes,
            },
          ];
          var layout = {
            height: 800,
            width: 800,
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
    xaxis: { title: xAxisTitle },
    yaxis: { title: yAxisTitle },
  };
  return layout;
}

function generateBarGraph(city, start, end, otherCities) {
  console.log(`other city ${otherCities}`);
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
            xaxis: { title: "Categories by City" },
            yaxis: { title: "Number of Crimes" },
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

function generateStackedBarGraph(city, start, end, otherCities) {
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

  fetch(
    `http://127.0.0.1:5000/crimes_stacked_bar_graph?city=${city}&start=${start}&end=${end}&otherCities=${JSON.stringify(
      { other_cities: otherCitiesList }
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

// // Takes in location from Geoapify address and will send data to mapchart
// pull.addEventListener("click", function () {
//     let cityName = mapChart.cityName;
//     // Don't get map data if there isn't an address
//     if (cityName == null){
//         return
//     }
//     let lat = mapChart.centerLat;
//     let lon = mapChart.centerLon;

//     let start = document.getElementById("start").value
//     let end = document.getElementById("end").value
//     let dropdownCity = document.getElementById("city").value
//     let radius = mapChart.getRadius();

//     // Assuming validation on server
//     fetch(`http://127.0.0.1:5000/crimes_from_address?dropdownCity=${dropdownCity}&cityName=${cityName}&start=${start}&end=${end}&radius=${radius}&lat=${lat}&lon=${lon}`)
//         .then((response) => {
//             return response.json();
//         })
//         .then((res) => {
//             if(res.errors.length){
//                 console.log(`Error: ${res.errors[0]}`)
//             }else{
//                 mapChart.sendData(res.features, res.center);
//                 let crimeScoreBox = document.getElementById("crime-score-box");
//                 crimeScoreBox.innerHTML = res.crimeScore;
//                 let crimeScoreBoxLabel = document.getElementById("crime-score-label");
//                 crimeScoreBoxLabel.innerHTML = res.crimeScoreLabel;

//                 let crimeRateBox = document.getElementById("crime-rate-box");
//                 crimeRateBox.innerHTML = res.crimeRate;
//                 let crimeRateBoxLabel = document.getElementById("crime-rate-label");
//                 crimeRateBoxLabel.innerHTML = res.crimeRateLabel;
//             }
//         });
// })

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
  mapChart = new MapChart("mapChart");
  let slider = document.getElementById("radRange");
  slider.onclick = function () {
    mapChart.setRadius(slider.value);
  };
});
