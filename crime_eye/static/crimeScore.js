//The inputs are:
//a location (City Center as an example)
//and a radius (r, 5 miles as an example):
//===============================
//PARAMETERS ARE
//Latitude
//Longitude
//Radius
//(we are letting user choose a radius, i can use whatever values, they will come from micah. use mock radii)

function renderBox(lat, long, radius) {
    let city = document.getElementById("city").value;
    console.log("CITY:", city, "LAT:", lat, "LONG:", long, "RADIUS:", radius);

    let address = "http://10.184.190.93:5000"
    let address2 = "http://127.0.0.1:5000"
    let fetchStr = `${address2}/get_crime_score?city=${city}&lat=${lat}&long=${long}&radius=${radius}`;
    fetch(fetchStr)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
           $(document).ready(function (){
                let crimeScoreBox = document.getElementById("crime-score-box");
                console.log("AT RENDER BOX:", data.crimeScore, crimeScoreBox);
                crimeScoreBox.innerHTML = data.crimeScore;
                //let box = '<div id="crimeScoreBox" value="">${crimeScore}</div>';
            })
        })
        .catch(error => alert(error.message));



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