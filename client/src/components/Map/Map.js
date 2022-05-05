import React, { Component } from "react";
import mapboxgl from "!mapbox-gl"; // eslint-disable-line import/no-webpack-loader-syntax
import "mapbox-gl/dist/mapbox-gl.css";
import "./styles.css";
import Row from "react-bootstrap/Row";

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN;

class Map extends Component {
  constructor(props) {
    super(props);
    this.state = {
      lng: -73.9066,
      lat: 40.7294,
      zoom: 9.5,
    };
    this.mapContainer = React.createRef();
  }

  componentDidMount() {
    const { lng, lat, zoom } = this.state;

    const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;

    // make map variable available outside of componentDidMount
    this.map = new mapboxgl.Map({
      container: this.mapContainer.current,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [lng, lat],
      zoom: zoom,
    });

    this.map.on("load", () => {
      console.log(this.map.getSource("manhattan"));
      // manhattan
      fetch(`${api_prefix}nta2020.geojson?boro_id=1`)
        .then((res) => res.json())
        .then((data) => {
          // console.dir(data);
          if (!this.map.getSource("manhattan")) {
            this.map.addSource("manhattan", {
              type: "geojson",
              data: data,
            });
          }
        });
      // bronx
      fetch(`${api_prefix}nta2020.geojson?boro_id=2`)
        .then((res) => res.json())
        .then((data) => {
          // console.dir(data);
          if (!this.map.getSource("bronx")) {
            this.map.addSource("bronx", {
              type: "geojson",
              data: data,
            });
          }
        });
      // brooklyn
      fetch(`${api_prefix}nta2020.geojson?boro_id=3`)
        .then((res) => res.json())
        .then((data) => {
          // console.dir(data);
          if (!this.map.getSource("brooklyn")) {
            this.map.addSource("brooklyn", {
              type: "geojson",
              data: data,
            });
          }
        });
      // queens
      fetch(`${api_prefix}nta2020.geojson?boro_id=4`)
        .then((res) => res.json())
        .then((data) => {
          // console.dir(data);
          if (!this.map.getSource("queens")) {
            this.map.addSource("queens", {
              type: "geojson",
              data: data,
            });
          }
        });
      // staten island
      fetch(`${api_prefix}nta2020.geojson?boro_id=5`)
        .then((res) => res.json())
        .then((data) => {
          // console.dir(data);
          if (!this.map.getSource("statenIsland")) {
            this.map.addSource("statenIsland", {
              type: "geojson",
              data: data,
            });
          }
        });

      // add 5 boroughs source
      // this.map.addSource("nyc-boroughs", {
      //   type: "geojson",
      //   data: boroughs,
      // });

      // add neighborhoods

      // add 5 boroughs layer
      // this.map.addLayer({
      //   id: "boroughs-viz",
      //   type: "fill",
      //   source: "nyc-boroughs",
      //   paint: {
      //     "fill-color": "#9ebcda",
      //   },
      // });
    });

    this.map.once("load", () => {
      this.map.resize();
    });
  }

  removeAllMapLayers(map) {
    if (map.getLayer("bronx-viz")) map.removeLayer("bronx-viz");
    if (map.getLayer("brooklyn-viz")) map.removeLayer("brooklyn-viz");
    if (map.getLayer("manhattan-viz")) map.removeLayer("manhattan-viz");
    if (map.getLayer("queens-viz")) map.removeLayer("queens-viz");
    if (map.getLayer("statenIsland-viz")) map.removeLayer("statenIsland-viz");
  }

  componentDidUpdate(prevProps) {
    if (prevProps.selectedBorough !== this.props.selectedBorough) {
      // console.dir(this.props.selectedBorough); prints object
      this.removeAllMapLayers(this.map);

      const lng = this.props.selectedBorough.lng;
      const lat = this.props.selectedBorough.lat;
      // eslint-disable-next-line default-case
      switch (this.props.selectedBorough.value) {
        case "Bronx":
          this.map.addLayer({
            id: "bronx-viz",
            type: "line",
            source: "bronx",
          });
          break;
        case "Brooklyn":
          this.map.addLayer({
            id: "brooklyn-viz",
            type: "line",
            source: "brooklyn",
          });
          break;
        case "Manhattan":
          this.map.addLayer({
            id: "manhattan-viz",
            type: "line",
            source: "manhattan",
          });
          break;
        case "Queens":
          this.map.addLayer({
            id: "queens-viz",
            type: "line",
            source: "queens",
          });
          break;
        case "Staten Island":
          this.map.addLayer({
            id: "statenIsland-viz",
            type: "line",
            source: "statenIsland",
          });
          break;
      }
      this.map.setCenter([lng, lat]);
      this.map.setZoom(10.5);
    }
  }

  render() {
    return (
      <Row className="mt-3 map-container">
        <div ref={this.mapContainer} />
      </Row>
    );
  }
}

export default Map;
