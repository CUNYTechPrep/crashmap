import React, { Component } from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import "./styles.css";

class Filter extends Component {
  render() {
    return (
      <Row id="filter">
        <Col xs={2}>
          <select name="" id="">
            <option value="" disabled selected hidden>
              Borough
            </option>
            <option value="manhattan">Manhattan</option>
            <option value="brooklyn">Brooklyn</option>
            <option value="queens">Queens</option>
            <option value="bronx">Bronx</option>
            <option value="staten island">Staten Island</option>
          </select>
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
