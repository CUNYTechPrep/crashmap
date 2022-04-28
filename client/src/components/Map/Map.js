import React, { Component } from "react";
import mapboxgl from "!mapbox-gl"; // eslint-disable-line import/no-webpack-loader-syntax
import "mapbox-gl/dist/mapbox-gl.css";
import "./styles.css";
import Row from "react-bootstrap/Row";

import boroughs from "./data/borough_boundaries.geojson";
import neighborhoods from "./data/2020_neighborhood_tabulation.geojson";

mapboxgl.accessToken =
  "pk.eyJ1Ijoic2VhbnlhcCIsImEiOiJjbDFmZnJjaHoxMTJ6M29zOXRoajZ0czlvIn0.BJC-KwTeHSCklDlBG9SEuQ";

class Map extends Component {
  constructor(props) {
    super(props);
    this.state = {
      lng: -73.9066,
      lat: 40.7294,
      zoom: 10,
    };
    this.mapContainer = React.createRef();
  }

  componentDidMount() {
    let bronxNeighborhoodGeojson = {
      name: "Bronx",
      type: "FeatureCollection",
      features: [],
    };
    let brooklynNeighborhoodGeojson = {
      name: "Brooklyn",
      type: "FeatureCollection",
      features: [],
    };
    let manhattanNeighborhoodGeojson = {
      name: "Manhattan",
      type: "FeatureCollection",
      features: [],
    };
    let queensNeighborhoodGeojson = {
      name: "Queens",
      type: "FeatureCollection",
      features: [],
    };
    let statenIslandNeighborhoodGeojson = {
      name: "StatenIsland",
      type: "FeatureCollection",
      features: [],
    };

    fetch(neighborhoods)
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        data.features.forEach((neighborhood) => {
          const borough = neighborhood.properties.boroname;
          // insert borough into geojson object
          switch (borough) {
            case "Bronx":
              bronxNeighborhoodGeojson.features.push(neighborhood);
              break;
            case "Brooklyn":
              brooklynNeighborhoodGeojson.features.push(neighborhood);
              break;
            case "Manhattan":
              manhattanNeighborhoodGeojson.features.push(neighborhood);
              break;
            case "Queens":
              queensNeighborhoodGeojson.features.push(neighborhood);
              break;
            case "Staten Island":
              statenIslandNeighborhoodGeojson.features.push(neighborhood);
              break;
            default:
              console.log("Borough Not Read: " + borough);
          }
        });
        // console.log(bronxNeighborhoodGeojson);
        // console.log(brooklynNeighborhoodGeojson);
        // console.log(manhattanNeighborhoodGeojson);
        // console.log(queensNeighborhoodGeojson);
        // console.log(statenIslandNeighborhoodGeojson);
      });

    const { lng, lat, zoom } = this.state;
    const map = new mapboxgl.Map({
      container: this.mapContainer.current,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [lng, lat],
      zoom: zoom,
    });
    map.on("load", () => {
      map.addSource("nyc-boroughs", {
        type: "geojson",
        data: boroughs,
        // url: "mapbox://seanyap.cl1pf13kw16kj20qxcol6dszx-117xf",
      });

      map.addLayer({
        id: "boroughs-viz",
        type: "fill",
        source: "nyc-boroughs",
        paint: {
          "fill-color": "#9ebcda",
        },
      });
    });

    map.once("load", () => {
      map.resize();
    });
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
