
//
//let pull = document.getElementById("pull");
//

//The inputs are:
//
//a location (City Center as an example)
//
//and a radius (r, 5 miles as an example):
//
//===============================
//
//PARAMETERS ARE
//
//Latitude
//
//Longitude
//
//Radius
//
//(we are letting user choose a radius, i can use whatever values, they will come from micah. use mock radii)

function renderBox(lat, long, radius) {
    let city = document.getElementById("city").value;
    console.log("CITY:", city);
    fetch(`http://127.0.0.1:5000/get_crime_score?city=${city}&lat=${lat}&long=${long}&radius=${radius}`)
        .then((response) => {

            console.log(response);
            return response.json();
        })
        .then((data) => {
            $(document).ready(function (){
                console.log(data);
            })
        })

//    let crimeScore = getCrimeScore(city, lat, long, radius);
//    let crimeScoreBox = document.getElementById("crime-score-box");
//    console.log("AT RENDER BOX:", crimeScore, crimeScoreBox);
//    crimeScoreBox.innerHTML = crimeScore;
    //let box = '<div id="crimeScoreBox" value="">${crimeScore}</div>';
}

function getEnteredInfo() {
    let city = document.getElementById("city").value
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    let radius = 3//mapChart.getRadius();
    let infoDict = {
                    "city": city,
                    "start": start,
                    "end": end,
                    "radius": radius
    }
    return infoDict;
}

pull.addEventListener("click", function () {
    let infoDict = getEnteredInfo();
    let lat = 1000;
    let long = 1000;
    let radius = infoDict["radius"];
    renderBox(lat, long, radius)
})