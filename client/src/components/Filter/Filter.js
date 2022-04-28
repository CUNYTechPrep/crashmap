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
  }

  currentBorough = (event) => {
    if (this.props.selectedOption)
      console.log("inside currentBorough: " + this.props.selectedOption.value);
    else console.log("inside currentBorough: nothing selected!");
  };

  render() {
    return (
      <Row id="filter">
        <Col xs={2}>
          {/* Borough Dropdown */}
          <Select
            value={this.props.selectedOption}
            onChange={this.props.handleBoroughChange}
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
