class MapChart{
    constructor(divName){
        // For storing info from address lookup
        this.cityName = null
        this.centerLat = null
        this.centerLon = null

        this.symbolLayerId;
        this.divName = divName;
        this.inFeatures = [];
        this.outFeatures = [];
        this.radius = 1; // Units in miles
        mapboxgl.accessToken = 'pk.eyJ1Ijoic3JhODQiLCJhIjoiY2w4ZjNmcXk4MDllbDQwbnpoOXJwa2VsZSJ9.OsLldCR-T9CjYaBE5Fa4OA';

        this.map = new mapboxgl.Map({
            container: 'mapChart',
            style: 'mapbox://styles/mapbox/dark-v11',
            center: [-97.62831376, 30.28096067],
            zoom: 10
        });

        this.map.on('load',()=>{
            const layers = this.map.getStyle().layers;
            // Find the index of the first symbol layer in the map style.
            for (const layer of layers) {
                if (layer.type === 'symbol') {
                    this.symbolLayerId = layer.id;
                    break;
                }
            }
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

    sendData(data, cityCenter){
        if(!data){
            return
        }

        // Locations
        // Adds the data
        this.map.getSource("inPoints").setData({
            type: 'FeatureCollection',
            features: data.inside
        });
        this.map.getSource("outPoints").setData({
            type: 'FeatureCollection',
            features: data.outside 
        });
        // Radius
        this.map.getSource("radius").setData(
            cityCenter.feature
        );
        
        
        // Draws the data
        if(!this.map.getLayer("inPoints")){
            this.map.addLayer({
                'id': 'inPoints',
                'type': 'circle',
                'source': 'inPoints',
                "paint": {
                    "circle-color": {
                        "property": 'crimeType',
                        "type": 'categorical',
                        "stops": [
                          ['Property', 'white'],
                          ['Person', 'blue'],
                          ['Society', 'yellow'],
                          ["Other", "brown"],
                          ["NotFound", "black"]
                        ]
                    },
                    "circle-opacity": 0.3
                    },
                },
                this.symbolLayerId);
        }
        // Draws the data
        if(!this.map.getLayer("outPoints")){
            this.map.addLayer({
                'id': 'outPoints',
                'type': 'circle',
                'source': 'outPoints',
                "paint": {
                    "circle-color": {
                        "property": 'crimeType',
                        "type": 'categorical',
                        "stops": [
                          ['Property', 'white'],
                          ['Person', 'blue'],
                          ['Society', 'yellow'],
                          ["Other", "brown"],
                          ["NotFound", "black"]
                        ]
                    },
                    "circle-opacity": 0.05,
                    }
                },
                this.symbolLayerId);
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
                center: cityCenter.coords, 
                essential: true
            }
        )

        // Results of data should be sent from server

    }
    resetCity(){
        this.cityName = null;
        this.centerLat = null;
        this.centerLon = null;
    }
    setAddressData(data){
        this.cityName = data.city
        this.centerLat = data.lat
        this.centerLon = data.lon
    }
}



