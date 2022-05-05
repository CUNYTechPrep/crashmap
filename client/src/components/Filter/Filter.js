import React, { Component } from 'react';
import Select from 'react-select';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import './styles.css';

const options = [
  { value: 'Bronx', label: 'BRONX', lng: '-73.865433', lat: '40.8448' },
  { value: 'Brooklyn', label: 'BROOKLYN', lng: '-73.9442', lat: '40.6782' },
  { value: 'Queens', label: 'QUEENS', lng: '-73.7949', lat: '40.7282' },
  { value: 'Manhattan', label: 'MANHATTAN', lng: '-73.9712', lat: '40.7831' },
  {
    value: 'Staten Island',
    label: 'STATEN ISLAND',
    lng: '-74.1502',
    lat: '40.5795',
  },
];

class Filter extends Component {
  // constructor(props) {
  //   super(props);
  // }

  currentBorough = (event) => {
    if (this.props.selectedBorough)
      console.log('inside currentBorough: ' + this.props.selectedBorough.value);
    else console.log('inside currentBorough: nothing selected!');
  };

  render() {
    return (
      <Row id='filter'>
        <Col xs={2}>
          {/* Borough Dropdown */}
          <Select
            value={this.props.selectedBorough}
            onChange={this.props.handleBoroughChange}
            options={options}
          />
        </Col>
        <Col xs={2}>
          <button className='btn btn-primary' onClick={this.currentBorough}>
            Enter city
          </button>

          {/* Neighborhood Dropdown */}
          {/* <select name="" id="" className="w-5">
            <option value="" disabled selected hidden>
              Neighborhood
            </option>
          </select> */}
        </Col>
      </Row>
    );
  }
}

export default Filter;
