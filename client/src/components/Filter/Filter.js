import React, { Component } from "react";
import Select from "react-select";
// import { Container } from "react-bootstrap";
import "./styles.css";
import ListGroup from "react-bootstrap/ListGroup";

const options = [
  { value: 2, label: "bronx", lng: "-73.865433", lat: "40.8448" },
  { value: 3, label: "brooklyn", lng: "-73.9442", lat: "40.6782" },
  { value: 4, label: "queens", lng: "-73.7949", lat: "40.7282" },
  { value: 1, label: "manhattan", lng: "-73.9712", lat: "40.7831" },
  {
    value: 5,
    label: "statenIsland",
    lng: "-74.1502",
    lat: "40.5795",
  },
];
function Rank(props) {
  return (
    <div>
      <ListGroup>
        <ListGroup.Item variant="primary" key={props.key}>
          {" "}
          {props.counter}. {props.name} : {props.total}
        </ListGroup.Item>
      </ListGroup>
    </div>
  );
}
class Filter extends Component {
  constructor(props) {
    super(props);
    this.state = {
      boroughSummary: [],
      borough: [],
    };
  }

  componentDidMount() {
    const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;
    let arr2 = [];
    let arr3 = [];
    fetch(
      `${api_prefix}boro_summary.json?boro_id=1&start_date=2020-01-01&end_date=2020-01-31`
    )
      .then(function (res) {
        return res.json();
      })
      .then((json) => {
        console.log(json);
        arr3 = {
          id: "1",
          collision: json[0].collisions,
          name: "Manhattan",
        };
        arr2.push(arr3);
        // console.log(arr3);
      });
    fetch(
      `${api_prefix}boro_summary.json?boro_id=2&start_date=2020-01-01&end_date=2020-01-31`
    )
      .then(function (res) {
        return res.json();
      })
      .then((json) => {
        console.log(json);
        arr3 = {
          id: "2",
          collision: json[0].collisions,
          name: "Bronx",
        };
        arr2.push(arr3);
        // console.log(arr2);
      });
    fetch(
      `${api_prefix}boro_summary.json?boro_id=3&start_date=2020-01-01&end_date=2020-01-31`
    )
      .then(function (res) {
        return res.json();
      })
      .then((json) => {
        console.log(json);
        arr3 = {
          id: "3",
          collision: json[0].collisions,
          name: "Brooklyn",
        };
        arr2.push(arr3);
        // console.log(arr2);
      });
    fetch(
      `${api_prefix}boro_summary.json?boro_id=4&start_date=2020-01-01&end_date=2020-01-31`
    )
      .then(function (res) {
        return res.json();
      })
      .then((json) => {
        console.log(json);
        arr3 = {
          id: "4",
          collision: json[0].collisions,
          name: "Queens",
        };
        arr2.push(arr3);
      });

    fetch(
      `${api_prefix}boro_summary.json?boro_id=5&start_date=2020-01-01&end_date=2020-01-31`
    )
      .then(function (res) {
        return res.json();
      })
      .then((json) => {
        console.log(json);
        arr3 = {
          id: "5",
          collision: json[0].collisions,
          name: "Staten Island",
        };
        arr2.push(arr3);

        // console.log(this.state.borough);
        let obj = [];
        let obj3 = [];

        // console.log(obj3);
        // console.log(obj);
        // console.log(arr2);
        this.setState({
          borough: arr2,
        });
        this.state.borough.sort((a, b) => {
          if (a.collision < b.collision) {
            return 1;
          } else {
            return -1;
          }
        });
        // console.log(arr2);

        // console.log(this.state.borough);

        this.setState({
          boroughSummary: this.state.borough,
        });
        // console.log(this.state.boroughSummary);
      });
  }
  currentBorough = (event) => {
    if (this.props.selectedBorough)
      console.log("inside currentBorough: " + this.props.selectedBorough.value);
    else console.log("inside currentBorough: nothing selected!");
  };

  render() {
    return (
      <div>
        <div className="option mb-3">
          <div className="card" style={{ width: "100%" }}>
            <ul className="list-group">
              <div className="col"></div>
              <li className="list-group-item">
                <p>View Neighborhood Boundaries</p>
                <Select
                  value={this.props.selectedBorough}
                  onChange={this.props.handleBoroughChange}
                  options={options}
                />
              </li>
            </ul>
          </div>
        </div>
        <div>
          <h5>Borough with Highest Collisions</h5>
          {this.state.boroughSummary.map((rank, i) => (
            <Rank
              counter={++i}
              key={rank.key}
              list={rank.boro_id}
              name={rank.name}
              total={rank.collision}
            ></Rank>
          ))}
        </div>
      </div>
    );
  }
}

export default Filter;
