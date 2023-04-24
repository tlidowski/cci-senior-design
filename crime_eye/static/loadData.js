let table_parent = document.getElementById("table_parent")
let pull = document.getElementById("pull")
let mapChart;

document.getElementById("nav-map-tab").addEventListener('shown.bs.tab', function () {
    mapChart.map.resize()
})


// Takes in location from Geoapify address and will send data to mapchart
pull.addEventListener("click", function () {
    let cityName = mapChart.cityName;
    // Don't get map data if there isn't an address
    if (cityName == null){
        return
    }
    let lat = mapChart.centerLat;
    let lon = mapChart.centerLon;

    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    let dropdownCity = document.getElementById("city").value
    let radius = mapChart.getRadius();


    // Assuming validation on server
    fetch(`http://127.0.0.1:5000/crimes_from_address?dropdownCity=${dropdownCity}&cityName=${cityName}&start=${start}&end=${end}&radius=${radius}&lat=${lat}&lon=${lon}`)
        .then((response) => {
            return response.json();
        })
        .then((res) => {
            if(res.errors.length){
                console.log(`Error: ${res.errors[0]}`)
            }else{
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
})


// pie graph
pull.addEventListener("click", function () {
    let city = document.getElementById("city").value
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    fetch(`http://127.0.0.1:5000/crimes_pie_chart?city=${city}&start=${start}&end=${end}`)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            $(document).ready(function (){
                // console.log(data.counts);
                var pieChart_data = [{
                    type: "pie",
                    values: data.counts,
                    labels: data.crimes
                }];
                var layout = {
                    height: 800,
                    width: 800
                  };
                Plotly.newPlot('pieChart',pieChart_data, layout);
            })
        })
})

// line graph
pull.addEventListener("click", function () {
    let city = document.getElementById("city").value
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    fetch(`http://127.0.0.1:5000/crimes_line_graph?city=${city}&start=${start}&end=${end}`)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            $(document).ready(function (){
                var countsByYearMonth = {}
                for (var i = 0; i < data.dates.length; i++) {
                    var splitDate = data.dates[i].split("/")
                    var year = parseInt(splitDate[1])
                    if (!isNaN(year)) {
                        var month = splitDate[0]
                        if (!countsByYearMonth[year]) {
                            countsByYearMonth[year] = {}
                        }
                        if (!countsByYearMonth[year][month]) {
                            countsByYearMonth[year][month] = 0
                        }
                        countsByYearMonth[year][month] += data.counts[i]
                    }
                }

                var lineGraph_data = []
                for (var year in countsByYearMonth) {
                    var x = []
                    var y = []
                    for (var month in countsByYearMonth[year]) {
                        x.push(getMonthName(parseInt(month)))
                        y.push(countsByYearMonth[year][month])
                    }

                    var monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    x.sort((a,b) => monthOrder.indexOf(a) - monthOrder.indexOf(b))
                    y.sort((a,b) => monthOrder.indexOf(x[y.indexOf(a)]) - monthOrder.indexOf(x[y.indexOf(b)]))

                    lineGraph_data.push({
                        type: "scatter",
                        y: y,
                        x: x,
                        name: year.toString()
                    })
                }

                var layout = {
                    title: 'Crime Timeline',
                    xaxis: {
                        title: 'Month'
                    },
                    yaxis: {
                        title: 'Number of Crimes',
                        rangemode: 'tozero'
                    }
                };

                Plotly.newPlot('lineGraph', lineGraph_data, layout);

            })
        })
})

function getMonthName(monthNum) {
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[monthNum - 1];
}

// bar graph
pull.addEventListener("click", function () {
    let city = document.getElementById("city").value
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    let city2 = document.getElementById("cityCompare").value

    if (city2 != null) {
        fetch(`http://127.0.0.1:5000/crimes_bar_graph?city=${city}&city2=${city2}&start=${start}&end=${end}`)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            $(document).ready(function (){
                var cityOne = {
                    type: "bar",
                    name: city,
                    y: data.counts,
                    x: data.crimes
                };
                var cityTwo = {
                    type: "bar",
                    name: city2,
                    y: data.counts2,
                    x: data.crimes2
                };
                var bar_data = [cityOne, cityTwo];
                var layout = {
                    barmode: 'group',
                    title: 'Comparison of Crimes Committed',
                    xaxis: { title: 'Categories by City' },
                    yaxis: { title: 'Number of Crimes'}
                };
                Plotly.newPlot('barGraph', bar_data, layout);
            })
        })
    }
})

window.addEventListener("load", ()=>{
    // Initialize map
    mapChart = new MapChart("mapChart");
    let slider = document.getElementById("radRange");
    slider.onclick =  function (){
        mapChart.setRadius(slider.value);
    };
})


