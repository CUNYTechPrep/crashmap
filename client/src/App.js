import React, { Component } from "react";
import Map from "./components/Map/Map.js";
import Filter from "./components/Filter/Filter.js";
import Overview from "./components/Filter/Overview.js";
import { Container } from "react-bootstrap";
// import LineChart from './components/LineChart.js';
import BarChart from "./components/BarChart/BarChart.js";

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

  // data = fetch('/api/boro.geojson')
  //   .then((response) => response.json())
  //   .then((data) => {
  //     console.log(data.data);
  //   });

  render() {
    return (
      <Container className="mt-5">
        <div className="container mt-5">
          <div className="row">
            <div className="col-9">
              <Overview
                className=""
                selectedBorough={this.state.selectedBorough}
              />
              <div id="hero">
                <Map
                  handleBoroughChange={this.handleBoroughChange.bind(this)}
                  selectedBorough={this.state.selectedBorough}
                />
              </div>
            </div>
            <div className="col-3">
              <Filter
                handleBoroughChange={this.handleBoroughChange.bind(this)}
                selectedBorough={this.state.selectedBorough}
              />
            </div>
          </div>

          <div className='barchart row'>
            <div className='col-6'>
              <BarChart
                // handleBoroughChange={this.handleBoroughChange.bind(this)}
                selectedBorough={this.state.selectedBorough}
              />
            </div>
            <div className='col-6'>pie chart</div>
          </div>
        </div>
      </Container>
    );
  }
}

export default App;
