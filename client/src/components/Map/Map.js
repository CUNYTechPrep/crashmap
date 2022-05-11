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
      lng: -73.98331400778511,
      lat: 40.70363951429806,
      zoom: 9.5,
      hoveredStateId: null,
    };
    this.mapContainer = React.createRef();
  }

  componentDidMount() {
    const { lng, lat, zoom } = this.state;

    const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;

    // make map variable available outside of componentDidMount
    this.map = new mapboxgl.Map({
      container: this.mapContainer.current,
      // style: "mapbox://styles/mapbox/streets-v11",
      style: "mapbox://styles/seanyap/cl31wio02000615ntvwn1rvd0",
      center: [lng, lat],
      zoom: zoom,
    });

    this.map.on("load", () => {
      console.log(this.map.getSource("manhattan"));
      // manhattan
      fetch(`${api_prefix}nta2020.geojson?id=MN____`)
        .then((res) => res.json())
        .then((data) => {
          const cloneData = JSON.parse(JSON.stringify(data));
          data.features.forEach((feature) => {
            feature.id = 1;
          });
          // console.dir(data);
          if (!this.map.getSource("manhattan")) {
            this.map.addSource("manhattan", {
              type: "geojson",
              data: data,
            });
            this.map.addLayer({
              id: "manhattan-fill",
              type: "fill",
              source: "manhattan",
              paint: {
                "fill-color": "#64B247",
                "fill-opacity": [
                  "case",
                  ["boolean", ["feature-state", "hover"], false],
                  0.7,
                  0.6,
                ],
              },
            });
          }
          if (!this.map.getSource("manhattan-neighborhoods")) {
            this.map.addSource("manhattan-neighborhoods", {
              type: "geojson",
              data: cloneData,
              generateId: true,
            });
          }
        });
      // bronx
      fetch(`${api_prefix}nta2020.geojson?id=BX____`)
        .then((res) => res.json())
        .then((data) => {
          const cloneData = JSON.parse(JSON.stringify(data));
          data.features.forEach((feature) => {
            feature.id = 2;
          });
          // console.dir(data);
          if (!this.map.getSource("bronx")) {
            this.map.addSource("bronx", {
              type: "geojson",
              data: data,
            });
            this.map.addLayer({
              id: "bronx-fill",
              type: "fill",
              source: "bronx",
              paint: {
                "fill-color": "#C07862",
                "fill-opacity": [
                  "case",
                  ["boolean", ["feature-state", "hover"], false],
                  0.7,
                  0.6,
                ],
              },
            });
          }
          if (!this.map.getSource("bronx-neighborhoods")) {
            this.map.addSource("bronx-neighborhoods", {
              type: "geojson",
              data: cloneData,
              generateId: true,
            });
          }
        });
      // brooklyn
      fetch(`${api_prefix}nta2020.geojson?id=BK____`)
        .then((res) => res.json())
        .then((data) => {
          const cloneData = JSON.parse(JSON.stringify(data));
          data.features.forEach((feature) => {
            feature.id = 3;
          });
          console.dir(data);
          if (!this.map.getSource("brooklyn")) {
            this.map.addSource("brooklyn", {
              type: "geojson",
              data: data,
            });
            this.map.addLayer({
              id: "brooklyn-fill",
              type: "fill",
              source: "brooklyn",
              paint: {
                "fill-color": "#627BC1",
                "fill-opacity": [
                  "case",
                  ["boolean", ["feature-state", "hover"], false],
                  0.7,
                  0.6,
                ],
              },
            });
          }
          if (!this.map.getSource("brooklyn-neighborhoods")) {
            this.map.addSource("brooklyn-neighborhoods", {
              type: "geojson",
              data: cloneData,
              generateId: true,
            });
          }
        });
      // queens
      fetch(`${api_prefix}nta2020.geojson?id=QN____`)
        .then((res) => res.json())
        .then((data) => {
          // console.dir(data);
          const cloneData = JSON.parse(JSON.stringify(data));
          data.features.forEach((feature) => {
            feature.id = 4;
          });
          if (!this.map.getSource("queens")) {
            this.map.addSource("queens", {
              type: "geojson",
              data: data,
            });
            this.map.addLayer({
              id: "queens-fill",
              type: "fill",
              source: "queens",
              paint: {
                "fill-color": "#C062AA",
                "fill-opacity": [
                  "case",
                  ["boolean", ["feature-state", "hover"], false],
                  0.7,
                  0.6,
                ],
              },
            });
          }
          if (!this.map.getSource("queens-neighborhoods")) {
            this.map.addSource("queens-neighborhoods", {
              type: "geojson",
              data: cloneData,
              generateId: true,
            });
          }
        });
      // staten island
      fetch(`${api_prefix}nta2020.geojson?id=SI____`)
        .then((res) => res.json())
        .then((data) => {
          // console.dir(data);
          const cloneData = JSON.parse(JSON.stringify(data));
          data.features.forEach((feature) => {
            feature.id = 5;
          });
          if (!this.map.getSource("statenIsland")) {
            this.map.addSource("statenIsland", {
              type: "geojson",
              data: data,
            });
            this.map.addLayer({
              id: "statenIsland-fill",
              type: "fill",
              source: "statenIsland",
              paint: {
                "fill-color": "#C0A762",
                "fill-opacity": [
                  "case",
                  ["boolean", ["feature-state", "hover"], false],
                  0.7,
                  0.6,
                ],
              },
            });
          }
          if (!this.map.getSource("statenIsland-neighborhoods")) {
            this.map.addSource("statenIsland-neighborhoods", {
              type: "geojson",
              data: cloneData,
              generateId: true,
            });
          }
        });

      // h3 hexagon /api/h3.geojson
      // fetch(`${api_prefix}h3.geojson?nta2020_id=MN`)
      //   .then((res) => res.json())
      //   .then((data) => {
      //     // console.dir(data);
      //     if (!this.map.getSource("h3")) {
      //       this.map.addSource("h3", {
      //         type: "geojson",
      //         data: data,
      //       });
      //     }
      //     if (!this.map.getLayer("h3-viz"))
      //       this.map.addLayer({
      //         id: "h3-viz",
      //         type: "line",
      //         source: "h3",
      //       });
      //   });
    });

    this.map.once("load", () => {
      this.map.resize();
    });

    const boroughNames = [
      "bronx",
      "brooklyn",
      "manhattan",
      "queens",
      "statenIsland",
    ];
    // add hover event listeners for each borough
    for (const name of boroughNames) {
      this.map.on("mousemove", `${name}-fill`, (e) => {
        this.map.getCanvas().style.cursor = "pointer";
        if (e.features.length > 0) {
          if (this.state.hoveredStateId !== null) {
            this.map.setFeatureState(
              { source: name, id: this.state.hoveredStateId },
              { hover: false }
            );
          }
          // console.log("inside mousemove " + name);
          this.setState({ hoveredStateId: e.features[0].id });
          this.map.setFeatureState(
            { source: name, id: this.state.hoveredStateId },
            { hover: true }
          );
        }
      });
      this.map.on("mouseleave", `${name}-fill`, () => {
        // console.log("inside mouseleave " + name);
        this.map.getCanvas().style.cursor = "";
        if (this.state.hoveredStateId !== null) {
          this.map.setFeatureState(
            { source: name, id: this.state.hoveredStateId },
            { hover: false }
          );
        }
        this.setState({ hoveredStateId: null });
      });
      this.map.on("click", `${name}-fill`, (e) => {
        const boroughCenters = [
          { value: "bronx", lng: "-73.865433", lat: "40.8448" },
          { value: "brooklyn", lng: "-73.9442", lat: "40.6782" },
          { value: "queens", lng: "-73.7949", lat: "40.7282" },
          { value: "manhattan", lng: "-73.9712", lat: "40.7831" },
          {
            value: "statenIsland",
            lng: "-74.1502",
            lat: "40.5795",
          },
        ];
        for (const center of boroughCenters) {
          if (center.value === name) this.props.handleBoroughChange(center);
        }
      });
    }
  }

  removeAllMapLayers(map) {
    if (map.getLayer("bronx-line")) map.removeLayer("bronx-line");
    if (map.getLayer("brooklyn-line")) map.removeLayer("brooklyn-line");
    if (map.getLayer("manhattan-line")) map.removeLayer("manhattan-line");
    if (map.getLayer("queens-line")) map.removeLayer("queens-line");
    if (map.getLayer("statenIsland-line")) map.removeLayer("statenIsland-line");
  }

  componentDidUpdate(prevProps) {
    if (prevProps.selectedBorough !== this.props.selectedBorough) {
      // console.dir(this.props.selectedBorough); prints object
      this.removeAllMapLayers(this.map);

      const lng = this.props.selectedBorough.lng;
      const lat = this.props.selectedBorough.lat;
      // eslint-disable-next-line default-case
      switch (this.props.selectedBorough.value) {
        case "bronx":
          this.map.addLayer({
            id: "bronx-line",
            type: "line",
            source: "bronx",
            paint: {
              "line-color": "#C07862",
              "line-width": 2,
            },
          });
          break;
        case "brooklyn":
          this.map.addLayer({
            id: "brooklyn-line",
            type: "line",
            source: "brooklyn",
            paint: {
              "line-color": "#627BC1",
              "line-width": 2,
            },
          });
          break;
        case "manhattan":
          this.map.addLayer({
            id: "manhattan-line",
            type: "line",
            source: "manhattan",
            paint: {
              "line-color": "#62B382",
              "line-width": 2,
            },
          });
          break;
        case "queens":
          this.map.addLayer({
            id: "queens-line",
            type: "line",
            source: "queens",
            paint: {
              "line-color": "#C062AA",
              "line-width": 2,
            },
          });
          break;
        case "statenIsland":
          this.map.addLayer({
            id: "statenIsland-line",
            type: "line",
            source: "statenIsland",
            paint: {
              "line-color": "#C0A762",
              "line-width": 2,
            },
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
