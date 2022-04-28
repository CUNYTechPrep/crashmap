import React, { Component } from "react";
import Select from "react-select";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import "./styles.css";

const options = [
  { value: "Bronx", label: "BRONX" },
  { value: "Brooklyn", label: "BROOKLYN" },
  { value: "Queens", label: "QUEENS" },
  { value: "Manhattan", label: "MANHATTAN" },
  { value: "Staten Island", label: "STATEN ISLAND" },
];

class Filter extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedOption: null,
    };
  }

  handleChange = (selectedOption) => {
    console.log("inside handleChange: " + selectedOption.value);
    //this.setState({radius: selectedOption.value})
    this.setState({ selectedOption });
  };

  currentBorough = (event) => {
    if (this.state.selectedOption)
      console.log("inside currentBorough: " + this.state.selectedOption.value);
    else console.log("inside currentBorough: nothing selected!");
  };

  render() {
    return (
      <Row id="filter">
        <Col xs={2}>
          {/* Borough Dropdown */}
          <Select
            value={this.state.selectedOption}
            onChange={this.handleChange}
            options={options}
          />
        </Col>
        <Col xs={2}>
          <button className="btn btn-primary" onClick={this.currentBorough}>
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
