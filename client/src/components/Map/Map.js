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
      neighborhoodHoveredStateId: null,
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
      // get all neighborhoods
      fetch(`${api_prefix}nta2020.geojson`)
        .then((res) => res.json())
        .then((data) => {
          // console.log("all neighborhoods below");
          const manhattan_nta = {
            features: data.features.filter(
              (nta) =>
                nta.properties.boro_id === 1 && nta.properties.name != null
            ),
            type: "FeatureCollection",
          };
          const bronx_nta = {
            features: data.features.filter(
              (nta) =>
                nta.properties.boro_id === 2 && nta.properties.name != null
            ),
            type: "FeatureCollection",
          };
          const brooklyn_nta = {
            features: data.features.filter(
              (nta) =>
                nta.properties.boro_id === 3 && nta.properties.name != null
            ),
            type: "FeatureCollection",
          };
          const queens_nta = {
            features: data.features.filter(
              (nta) =>
                nta.properties.boro_id === 4 && nta.properties.name != null
            ),
            type: "FeatureCollection",
          };
          const statenIsland_nta = {
            features: data.features.filter(
              (nta) =>
                nta.properties.boro_id === 5 && nta.properties.name != null
            ),
            type: "FeatureCollection",
          };

          function countCollisions(data, nta) {
            const collisions = data.filter(
              (collision) => collision.nta2020_id === nta.properties.id
            );
            let count = 0;
            for (const collision of collisions) count += collision.collisions;
            return count;
          }

          // get all boroughs
          fetch(`${api_prefix}boro.geojson`)
            .then((res) => res.json())
            .then((data) => {
              // console.log("all boroughs below");
              const manhattan = data.features[0];
              manhattan.geometry = manhattan.properties.land_geometry; // remove waters
              const bronx = data.features[1];
              bronx.geometry = bronx.properties.land_geometry; // remove waters
              const brooklyn = data.features[2];
              brooklyn.geometry = brooklyn.properties.land_geometry; // remove waters
              const queens = data.features[3];
              queens.geometry = queens.properties.land_geometry; // remove waters
              const statenIsland = data.features[4];
              statenIsland.geometry = statenIsland.properties.land_geometry; // remove waters

              // setting id for mapbox hover state
              manhattan.id = 1;
              bronx.id = 2;
              brooklyn.id = 3;
              queens.id = 4;
              statenIsland.id = 5;

              // render manhattan borough
              if (!this.map.getSource("manhattan")) {
                this.map.addSource("manhattan", {
                  type: "geojson",
                  data: manhattan,
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
              // render bronx borough
              if (!this.map.getSource("bronx")) {
                this.map.addSource("bronx", {
                  type: "geojson",
                  data: bronx,
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
              // render brooklyn borough
              if (!this.map.getSource("brooklyn")) {
                this.map.addSource("brooklyn", {
                  type: "geojson",
                  data: brooklyn,
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
              // render queens borough
              if (!this.map.getSource("queens")) {
                this.map.addSource("queens", {
                  type: "geojson",
                  data: queens,
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
              // render statenIsland borough
              if (!this.map.getSource("statenIsland")) {
                this.map.addSource("statenIsland", {
                  type: "geojson",
                  data: statenIsland,
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
            });

          fetch(`${api_prefix}nta2020_summary.json`)
            .then((res) => res.json())
            .then((data) => {
              manhattan_nta.features.forEach((nta) => {
                nta.properties.collisionCount = countCollisions(data, nta);
              });
              bronx_nta.features.forEach((nta) => {
                nta.properties.collisionCount = countCollisions(data, nta);
              });
              brooklyn_nta.features.forEach((nta) => {
                nta.properties.collisionCount = countCollisions(data, nta);
              });
              queens_nta.features.forEach((nta) => {
                nta.properties.collisionCount = countCollisions(data, nta);
              });
              statenIsland_nta.features.forEach((nta) => {
                nta.properties.collisionCount = countCollisions(data, nta);
              });
              // console.dir(manhattan_nta);
              if (!this.map.getSource("manhattan-neighborhoods")) {
                this.map.addSource("manhattan-neighborhoods", {
                  type: "geojson",
                  data: manhattan_nta,
                  generateId: true,
                });
              }
              if (!this.map.getSource("bronx-neighborhoods")) {
                this.map.addSource("bronx-neighborhoods", {
                  type: "geojson",
                  data: bronx_nta,
                  generateId: true,
                });
              }
              if (!this.map.getSource("brooklyn-neighborhoods")) {
                this.map.addSource("brooklyn-neighborhoods", {
                  type: "geojson",
                  data: brooklyn_nta,
                  generateId: true,
                });
              }
              if (!this.map.getSource("queens-neighborhoods")) {
                this.map.addSource("queens-neighborhoods", {
                  type: "geojson",
                  data: queens_nta,
                  generateId: true,
                });
              }
              if (!this.map.getSource("statenIsland-neighborhoods")) {
                this.map.addSource("statenIsland-neighborhoods", {
                  type: "geojson",
                  data: statenIsland_nta,
                  generateId: true,
                });
              }
            });
        });

      // h3 hexagon /api/h3.geojson
      // fetch(`${api_prefix}h3.geojson?nta2020_id=BK&only_water=false`)
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
            { value: 2, label: "bronx", lng: "-73.865433", lat: "40.8448" },
            { value: 3, label: "brooklyn", lng: "-73.9442", lat: "40.6782" },
            { value: 4, label: "queens", lng: "-73.7949", lat: "40.7282" },
            { value: 1, label: "manhattan", lng: "-73.9712", lat: "40.7831" },
            {
              value: 5,
              label: "statenIsland",
              lng: "-74.1502",
              lat: "40.5795",
            },
          ];
          for (const center of boroughCenters) {
            if (center.label === name) this.props.handleBoroughChange(center);
          }
        });

        // add a mousemove and mouseleave event listeners for every neighborhood (for hover effect)
        const popup = new mapboxgl.Popup({
          closeButton: false,
          closeOnClick: false,
        });
        // hover for borough's neighborhoods
        this.map.on("mousemove", `${name}-neighborhoods-fill`, (e) => {
          this.map.getCanvas().style.cursor = "pointer";
          // if (e.features.length > 0) {
          //   if (this.state.neighborhoodHoveredStateId !== null) {
          //     this.map.setFeatureState(
          //       {
          //         source: `${name}-neighborhoods`,
          //         id: this.state.neighborhoodHoveredStateId,
          //       },
          //       { hover: false }
          //     );
          //   }
          //   this.setState({ neighborhoodHoveredStateId: e.features[0].id });
          //   this.map.setFeatureState(
          //     {
          //       source: `${name}-neighborhoods`,
          //       id: this.state.neighborhoodHoveredStateId,
          //     },
          //     { hover: true }
          //   );
          // }

          const ntaName = e.features[0].properties.name;
          const coordLen = e.features[0].properties.representative_point.length;
          const lngLat = e.features[0].properties.representative_point
            .slice(1, coordLen - 1)
            .split(",");
          const coordinates = new mapboxgl.LngLat(lngLat[0], lngLat[1]);
          const collisionCount = e.features[0].properties.collisionCount;

          const description = `<strong>${ntaName}</strong><p>Collision: ${collisionCount}</p>`;

          popup.setLngLat(coordinates).setHTML(description).addTo(this.map);
        });
        this.map.on("mouseleave", `${name}-neighborhoods-fill`, () => {
          // console.log(`outside ${name}'s neighborhoods`);
          this.map.getCanvas().style.cursor = "";
          // if (this.state.neighborhoodHoveredStateId !== null) {
          //   this.map.setFeatureState(
          //     {
          //       source: `${name}-neighborhoods`,
          //       id: this.state.neighborhoodHoveredStateId,
          //     },
          //     { hover: false }
          //   );
          // }
          this.setState({ neighborhoodHoveredStateId: null });
          popup.remove();
        });
      }
    });

    this.map.once("load", () => {
      this.map.resize();
    });
  }

  resetMapLayers() {
    if (this.map.getLayer("bronx-line")) this.map.removeLayer("bronx-line");
    if (this.map.getLayer("brooklyn-line"))
      this.map.removeLayer("brooklyn-line");
    if (this.map.getLayer("manhattan-line"))
      this.map.removeLayer("manhattan-line");
    if (this.map.getLayer("queens-line")) this.map.removeLayer("queens-line");
    if (this.map.getLayer("statenIsland-line"))
      this.map.removeLayer("statenIsland-line");

    if (this.map.getLayer("bronx-neighborhoods-fill"))
      this.map.removeLayer("bronx-neighborhoods-fill");
    if (this.map.getLayer("brooklyn-neighborhoods-fill"))
      this.map.removeLayer("brooklyn-neighborhoods-fill");
    if (this.map.getLayer("manhattan-neighborhoods-fill"))
      this.map.removeLayer("manhattan-neighborhoods-fill");
    if (this.map.getLayer("queens-neighborhoods-fill"))
      this.map.removeLayer("queens-neighborhoods-fill");
    if (this.map.getLayer("statenIsland-neighborhoods-fill"))
      this.map.removeLayer("statenIsland-neighborhoods-fill");

    // add back fill layer after it is deleted when user click a borough
    if (!this.map.getLayer("bronx-fill"))
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
    if (!this.map.getLayer("brooklyn-fill"))
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
            0.5,
          ],
        },
      });
    if (!this.map.getLayer("manhattan-fill"))
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
    if (!this.map.getLayer("queens-fill"))
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
    if (!this.map.getLayer("statenIsland-fill"))
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

  componentDidUpdate(prevProps) {
    if (prevProps.selectedBorough !== this.props.selectedBorough) {
      // console.dir(this.props.selectedBorough); prints object
      this.resetMapLayers();

      const lng = this.props.selectedBorough.lng;
      const lat = this.props.selectedBorough.lat;
      // eslint-disable-next-line default-case
      switch (this.props.selectedBorough.label) {
        case "bronx":
          this.map.addLayer({
            id: "bronx-line",
            type: "line",
            source: "bronx-neighborhoods",
            paint: {
              "line-color": "#C07862",
              "line-width": 2,
            },
          });
          if (this.map.getLayer("bronx-fill"))
            this.map.removeLayer("bronx-fill");
          this.map.addLayer({
            id: "bronx-neighborhoods-fill",
            type: "fill",
            source: "bronx-neighborhoods",
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
          break;
        case "brooklyn":
          this.map.addLayer({
            id: "brooklyn-line",
            type: "line",
            source: "brooklyn-neighborhoods",
            paint: {
              "line-color": "#627BC1",
              "line-width": 2,
            },
          });
          if (this.map.getLayer("brooklyn-fill"))
            this.map.removeLayer("brooklyn-fill");
          this.map.addLayer({
            id: "brooklyn-neighborhoods-fill",
            type: "fill",
            source: "brooklyn-neighborhoods",
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
          console.log("Added neighborhoods layer");
          break;
        case "manhattan":
          this.map.addLayer({
            id: "manhattan-line",
            type: "line",
            source: "manhattan-neighborhoods",
            paint: {
              "line-color": "#62B382",
              "line-width": 2,
            },
          });
          if (this.map.getLayer("manhattan-fill"))
            this.map.removeLayer("manhattan-fill");
          this.map.addLayer({
            id: "manhattan-neighborhoods-fill",
            type: "fill",
            source: "manhattan-neighborhoods",
            paint: {
              "fill-color": "#62B382",
              "fill-opacity": [
                "case",
                ["boolean", ["feature-state", "hover"], false],
                0.7,
                0.6,
              ],
            },
          });
          break;
        case "queens":
          this.map.addLayer({
            id: "queens-line",
            type: "line",
            source: "queens-neighborhoods",
            paint: {
              "line-color": "#C062AA",
              "line-width": 2,
            },
          });
          if (this.map.getLayer("queens-fill"))
            this.map.removeLayer("queens-fill");
          this.map.addLayer({
            id: "queens-neighborhoods-fill",
            type: "fill",
            source: "queens-neighborhoods",
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
          break;
        case "statenIsland":
          this.map.addLayer({
            id: "statenIsland-line",
            type: "line",
            source: "statenIsland-neighborhoods",
            paint: {
              "line-color": "#C0A762",
              "line-width": 2,
            },
          });
          if (this.map.getLayer("statenIsland-fill"))
            this.map.removeLayer("statenIsland-fill");
          this.map.addLayer({
            id: "statenIsland-neighborhoods-fill",
            type: "fill",
            source: "statenIsland-neighborhoods",
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
