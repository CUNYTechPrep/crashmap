import React, { Component } from "react";
import Map from "./components/Map/Map.js";
import Filter from "./components/Filter/Filter.js";
import { Container } from "react-bootstrap";

import "./App.css";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedOption: null,
    };
  }

  handleBoroughChange(selectedOption) {
    console.log("inside handleChange: " + selectedOption.value);
    //this.setState({radius: selectedOption.value})
    this.setState({ selectedOption });
  }

  render() {
    return (
      <Container className="mt-5">
        <div id="hero">
          <Filter
            handleBoroughChange={this.handleBoroughChange.bind(this)}
            selectedOption={this.state.selectedOption}
          />
          <Map />
        </div>
      </Container>
    );
  }
}

export default App;
