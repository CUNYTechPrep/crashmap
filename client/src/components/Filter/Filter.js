import React, { Component } from "react";
import Select from "react-select";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import "./styles.css";

const options = [
  { value: 2, label: 'Bronx', lng: '-73.865433', lat: '40.8448' },
  { value: 3, label: 'Brooklyn', lng: '-73.9442', lat: '40.6782' },
  { value: 4, label: 'Queens', lng: '-73.7949', lat: '40.7282' },
  { value: 1, label: 'Manhattan', lng: '-73.9712', lat: '40.7831' },
  {
    value: 5,
    label: 'Staten Island',
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
      console.log("inside currentBorough: " + this.props.selectedBorough.value);
    else console.log("inside currentBorough: nothing selected!");
  };

  render() {
    return (
      <div>
        <div className='option border border-3 border-primary rounded  p-3 mb-3'>
          <div className='card row'>
            <ul className=' list-group list-group-flush'>
              <div className='col'></div>
      <li className='list-group-item' >
       <p>View Neighborhood Boundaries</p>
       <Select
            value={this.props.selectedBorough}
            onChange={this.props.handleBoroughChange}
            options={options}
          />
            <button className='btn btn-primary' onClick={this.currentBorough}>
            Enter city
          </button>
  
       
      </li>
      </ul>
   
      </div>
      </div>
      </div>
    );
  }
}

export default Filter;
