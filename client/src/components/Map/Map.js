import React, { Component } from 'react';
import mapboxgl from '!mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax
import 'mapbox-gl/dist/mapbox-gl.css';
import './styles.css';
import Row from 'react-bootstrap/Row';

import boroughs from './data/borough_boundaries.geojson';

mapboxgl.accessToken =
  'pk.eyJ1Ijoic2VhbnlhcCIsImEiOiJjbDFmZnJjaHoxMTJ6M29zOXRoajZ0czlvIn0.BJC-KwTeHSCklDlBG9SEuQ';

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
    const { lng, lat, zoom } = this.state;
    const map = new mapboxgl.Map({
      container: this.mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [lng, lat],
      zoom: zoom,
    });
    map.on('load', () => {
      map.addSource('nyc-boroughs', {
        type: 'geojson',
        data: boroughs,
        // url: "mapbox://seanyap.cl1pf13kw16kj20qxcol6dszx-117xf",
      });

      map.addLayer({
        id: 'boroughs-viz',
        type: 'line',
        source: 'nyc-boroughs',
        paint: {
          'line-color': [
            'match',
            ['get', 'boro_name'],
            'Queens',
            '#67009e',
            'Manhattan',
            '#96228e',
            'Bronx',
            '#e89c4f',
            'Brooklyn',
            '#d36d64',
            'Staten Island',
            '#b9467a',
            'black',
          ],
          'line-width': 2.5,
        },
      });
    });

    map.once('load', () => {
      map.resize();
    });
  }

  render() {
    return (
      <Row className='mt-3 map-container'>
        <div ref={this.mapContainer} />
      </Row>
    );
  }
}

export default Map;
