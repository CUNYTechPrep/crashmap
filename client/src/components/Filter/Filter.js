import React, { Component } from "react";
import Select from 'react-select';
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import "./styles.css";



const options = [
  { value: 'Bronx', label: 'BRONX' },
  { value: 'Brooklyn', label: 'BROOKLYN' },
  { value: 'Queens', label: 'QUEENS' },
  { value: 'Manhattan', label: 'MANHATTAN' },
  { value: 'Staten Island', label: 'STATEN ISLAND' },
]
class Filter extends Component {
  state ={
    selectedOption: null
  }
  handleChange = (selectedOption) => {
    console.log(selectedOption.value)
    //this.setState({radius: selectedOption.value})
    this.setState({ selectedOption, }, () =>
      console.log(`Option selected:`, this.state.selectedOption.label)

    );
  };

   
  currentBorough = (event) => { 
    console.log(this.state.selectedOption)
  }
  render() {
    const { selectedOption } = this.state;
    return (
      
      <Row id="filter">
        <Col xs={2}>
        <Select
          value={selectedOption}
          onChange={this.handleChange}
          options={options}
        />
            <button className="btn btn-primary" onClick={this.currentBorough}>Enter city</button>
        </Col>
        <Col xs={2}>
          <select name="" id="" className="w-5">
            <option value="" disabled selected hidden>
              Neighborhood
            </option>
          </select>
        </Col>
    
      </Row>
    );
  }
}

export default Filter;
