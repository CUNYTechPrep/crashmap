import React, { Component } from "react";
import Map from "./components/Map/Map.js";
import Filter from "./components/Filter/Filter.js";
import { Container } from "react-bootstrap";

import "./App.css";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedBorough: null,
    };
  }

  handleBoroughChange(selectedBorough) {
    console.log("inside handleChange: " + selectedBorough.value);
    //this.setState({radius: selectedOption.value})
    this.setState({ selectedBorough });
  }

  render() {
    return (
      <Container className="mt-5">
        <div id="hero">
          <Filter
            handleBoroughChange={this.handleBoroughChange.bind(this)}
            selectedBorough={this.state.selectedBorough}
          />
          <Map
            handleBoroughChange={this.handleBoroughChange.bind(this)}
            selectedBorough={this.state.selectedBorough}
          />
        </div>
      </Container>
    );
  }
}

export default App;
