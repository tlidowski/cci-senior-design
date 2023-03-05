class MapChart{
    constructor(divName){
        this.divName = divName;
        this.inFeatures = [];
        this.outFeatures = [];
        this.radius = 3; // Units in pixels
        this.map = new mapboxgl.Map({
            container: 'mapChart',
            style: 'mapbox://styles/mapbox/dark-v11',
            center: [-97.62831376, 30.28096067],
            zoom: 10
        });

        this.map.on('load',()=>{
        // Initialize Sources (Used to store points on map)
            this.map.addSource("inPoints",{
                type:'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: [] 
                }
            })

            this.map.addSource("outPoints",{
                type:'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: [] 
                }
            })
            
            // Radius [Points will be generated based of the city location]
            this.map.addSource("radius",{
                type:'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: [] 
                }
            })
        })
        
    }
    getRadius(){
        return this.radius;
    }

    setRadius(val){
        this.radius = val;
    }

    resetData(){
        this.inFeatures = [];
        this.outFeatures = [];
    }

    sendData(data, cityCenter){
        if(!data){
            return
        }
        // Process Data 
        // TODO, the features could be done server side as well, not just the lat/lon aggregation
        this.resetData();
        data.inside.forEach(location => {

            this.inFeatures.push({
                "type": 'Feature',
                "geometry" : {
                    "type": "Point",
                    "coordinates": location
                },
                "properties": {
                    "description": "CRIME TYPE"
                },
            }
            )
        });

        data.outside.forEach(location => {
            this.outFeatures.push({
                "type": 'Feature',
                "geometry" : {
                    "type": "Point",
                    "coordinates":location
                },
                "properties": {
                    "description": "CRIME TYPE"
                },
            }
            )
        });

        // Locations
        // Adds the data
        this.map.getSource("inPoints").setData({
            type: 'FeatureCollection',
            features: this.inFeatures 
        });
        this.map.getSource("outPoints").setData({
            type: 'FeatureCollection',
            features: this.outFeatures 
        });
        
        // Radius
        this.map.getSource("radius").setData(
            this.generateRadiusGeoJson(cityCenter, this.radius)
        );
        
        
        // Draws the data
        if(!this.map.getLayer("inPoints")){
            this.map.addLayer({
                'id': 'inPoints',
                'type': 'circle',
                'source': 'inPoints',
                "paint": {
                    "circle-color": "red",
                    "circle-opacity": 0.2
                    },
                "icon-allow-overlap":true, 
                "text-allow-overlap":true,
                });
        }

        // Draws the data
        if(!this.map.getLayer("outPoints")){
            this.map.addLayer({
                'id': 'outPoints',
                'type': 'circle',
                'source': 'outPoints',
                "paint": {
                    "circle-color": "yellow",
                    "circle-opacity": 0.2,
                    }
                });
        }

        if(!this.map.getLayer("radius")){
            this.map.addLayer({
            'id': 'radius',
            'type': 'fill',
            'source': 'radius',
            "paint": {
                "fill-color": "#808080",
                "fill-opacity": 0.4
              }
            });
        }
        // Centers map to location
        this.map.flyTo(
            {
                center: cityCenter, // Might need to be swapped
                essential: true
            }
        )

        this.printResults()

    }

    printResults(){
        // Should prob also be done on server
        let inAmount = this.inFeatures.length;
        let outAmount = this.outFeatures.length;
        let percent = ((inAmount / (inAmount + outAmount)) * 100).toFixed(2);
        console.log(`% Inside ${this.radius}-Mile Radius  = ${percent}%`);
    }
    // https://stackoverflow.com/questions/37599561/drawing-a-circle-with-the-radius-in-miles-meters-with-mapbox-gl-js
    // Creates radius relative to view
    generateRadiusGeoJson(center, radiusInMiles, points){
        if(!points) points = 64;

        var coords = {
            latitude: center[1],
            longitude: center[0]
        };
    
        var km = radiusInMiles * 1.609344;
    
        var ret = [];
        var distanceX = km/(111.320*Math.cos(coords.latitude*Math.PI/180));
        var distanceY = km/110.574;
    
        var theta, x, y;
        for(var i=0; i<points; i++) {
            theta = (i/points)*(2*Math.PI);
            x = distanceX*Math.cos(theta);
            y = distanceY*Math.sin(theta);
    
            ret.push([coords.longitude+x, coords.latitude+y]);
        }
        ret.push(ret[0]);
    
        return {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [ret]
                }
            }]
        }
    
    }
}



