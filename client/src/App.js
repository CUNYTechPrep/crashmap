import React, { Component } from 'react';
import Map from './components/Map/Map.js';
import Filter from './components/Filter/Filter.js';
import Overview from './components/Filter/Overview.js';
import { Container } from 'react-bootstrap';
// import LineChart from './components/LineChart.js';
import LineChart from './components/BarChart/LineChart.js';
import BarChart from './components/BarChart/BarChart.js';

import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedBorough: null,
    };
  }

  handleBoroughChange(selectedBorough) {
    console.log('inside handleChange: ' + selectedBorough.value);
    //this.setState({radius: selectedOption.value})
    this.setState({ selectedBorough });
  }

  render() {
    return (
      <Container className='mt-5'>
        <div className='container mt-5'>
          <div className='row'>
            <div className='col-9'>
              <Overview
                className=''
                selectedBorough={this.state.selectedBorough}
              />
              <div id='hero'>
                <Map
                  handleBoroughChange={this.handleBoroughChange.bind(this)}
                  selectedBorough={this.state.selectedBorough}
                />
              </div>
            </div>
            <div className='col-3'>
              <Filter
                handleBoroughChange={this.handleBoroughChange.bind(this)}
                selectedBorough={this.state.selectedBorough}
              />
              <BarChart
                // handleBoroughChange={this.handleBoroughChange.bind(this)}
                selectedBorough={this.state.selectedBorough}
              />
            </div>
          </div>
        </div>
      </Container>
    );
  }
}

export default App;
