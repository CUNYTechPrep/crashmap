import React from "react";
import { Line, Bar, Pie, Doughnut } from "react-chartjs-2";
import Chart from "chart.js/auto";
import "./styles.css";

class BoroChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      visibility: "hide",
      boroughs: [],
      curr: [
        {
          id: "",
          collision: 0,
          cyclists: 0,
          cyclists_injured: 0,
          cyclists_killed: 0,
          ped: 0,
          ped_injured: 0,
          ped_killed: 0,
          car_occupants: 0,
          car_occupants_injured: 0,
          car_occupants_killed: 0,
          collisions: 0,
          name: "",
        },
      ],
    };
  }

  componentDidMount() {
    //   console.log('line', this.props.selectedBorough);
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
        // console.log(json);
        arr3 = {
          id: "1",
          collision: json[0].collisions,
          cyclists: json[0].cyclists,
          cyclists_injured: json[0].cyclists_injured,
          cyclists_killed: json[0].cyclists_killed,
          ped: json[0].pedestrians,
          ped_injured: json[0].pedestrians_injured,
          ped_killed: json[0].pedestrians_killed,
          car_occupants: json[0].occupants,
          car_occupants_injured: json[0].occupants_injured,
          car_occupants_killed: json[0].occupants_killed,
          collisions: json[0].collisions,
          name: "Manhattan",
        };
        // this.setState({ mn: arr3 });
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
        // console.log(json);
        arr3 = {
          id: "2",
          collision: json[0].collisions,
          cyclists: json[0].cyclists,
          cyclists_injured: json[0].cyclists_injured,
          cyclists_killed: json[0].cyclists_killed,
          ped: json[0].pedestrians,
          ped_injured: json[0].pedestrians_injured,
          ped_killed: json[0].pedestrians_killed,
          car_occupants: json[0].occupants,
          car_occupants_injured: json[0].occupants_injured,
          car_occupants_killed: json[0].occupants_killed,
          collisions: json[0].collisions,
          name: "Bronx",
        };
        // this.setState({ bx: arr3 });
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
        // console.log(json);
        arr3 = {
          id: "3",
          collision: json[0].collisions,
          cyclists: json[0].cyclists,
          cyclists_injured: json[0].cyclists_injured,
          cyclists_killed: json[0].cyclists_killed,
          ped: json[0].pedestrians,
          ped_injured: json[0].pedestrians_injured,
          ped_killed: json[0].pedestrians_killed,
          car_occupants: json[0].occupants,
          car_occupants_injured: json[0].occupants_injured,
          car_occupants_killed: json[0].occupants_killed,
          collisions: json[0].collisions,
          name: "Brooklyn",
        };
        // this.setState({ bk: arr3 });
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
        // console.log(json);
        arr3 = {
          id: "4",
          collision: json[0].collisions,
          cyclists: json[0].cyclists,
          cyclists_injured: json[0].cyclists_injured,
          cyclists_killed: json[0].cyclists_killed,
          ped: json[0].pedestrians,
          ped_injured: json[0].pedestrians_injured,
          ped_killed: json[0].pedestrians_killed,
          car_occupants: json[0].occupants,
          car_occupants_injured: json[0].occupants_injured,
          car_occupants_killed: json[0].occupants_killed,
          collisions: json[0].collisions,
          name: "Queens",
        };
        // this.setState({ qn: arr3 });
        arr2.push(arr3);
      });

    fetch(
      `${api_prefix}boro_summary.json?boro_id=5&start_date=2020-01-01&end_date=2020-01-31`
    )
      .then(function (res) {
        return res.json();
      })
      .then((json) => {
        // console.log(json);
        arr3 = {
          id: "5",
          collision: json[0].collisions,
          cyclists: json[0].cyclists,
          cyclists_injured: json[0].cyclists_injured,
          cyclists_killed: json[0].cyclists_killed,
          ped: json[0].pedestrians,
          ped_injured: json[0].pedestrians_injured,
          ped_killed: json[0].pedestrians_killed,
          car_occupants: json[0].occupants,
          car_occupants_injured: json[0].occupants_injured,
          car_occupants_killed: json[0].occupants_killed,
          collisions: json[0].collisions,
          name: "Staten Island",
        };
        // this.setState({ si: arr3 });
        // console.log(this.state.mn);
        arr2.push(arr3);

        this.setState({
          boroughs: arr2,
          // curr: arr2,
        });
      });
  }

  componentDidUpdate(prevProps) {
    if (this.props.selectedBorough !== null) {
      if (this.state.visibility === "hide") {
        this.setState({ visibility: "show" });
      }
    }
    if (prevProps.selectedBorough !== this.props.selectedBorough) {
      console.log("prevProps.selectedBorough", prevProps.selectedBorough);
      console.log("this.props.selectedBorough", this.props.selectedBorough);
      for (var i = 0; i < 5; i++) {
        if (
          parseInt(this.state.boroughs[i].id) ===
          this.props.selectedBorough.value
        ) {
          console.log("in for loop", this.state.boroughs[i]);
          this.setState({ curr: this.state.boroughs[i] });
        }
      }

      // });
    }
  }

  render() {
    return (
      <div className={`${this.state.visibility}`}>
        {/* <h5 className='title'>
          {this.state.curr?.name}: {this.state.curr?.collisions}
        </h5> */}
        <Doughnut
          style={{ marginTop: "5px" }}
          data={{
            // x-axis label values
            labels: [
              "Cyclists Injured",
              // 'Cyclists Killed',
              "Pedestrians Injured",
              // 'Pedestrians Killed',
              "Vehicle Occupants Injured",
              // 'Vehicle Occupant Killed',
            ],
            datasets: [
              {
                label: `Total Cyclists and Pedestrians Involved`,
                // y-axis data plotting values
                data: [
                  // `${this.state.curr?.cyclists}`,
                  `${this.state.curr?.cyclists_injured}`,
                  // `${this.state.curr?.cyclists_killed}`,

                  // `${this.state.curr?.ped}`,
                  `${this.state.curr?.ped_injured}`,
                  // `${this.state.curr?.ped_killed}`,

                  `${this.state.curr?.car_occupants_injured}`,
                  // `${this.state.curr?.car_occupants_killed}`,
                ],
                fill: false,
                borderWidth: 0.5,
                backgroundColor: [
                  "rgba(100,178,71,1)",
                  // 'rgba(132, 169, 117,1)',
                  "rgba(106, 90, 205,1)",
                  // 'rgba(230,120,98, 1)',
                  "rgba(238, 130, 238,1)",
                  // 'rgba(218, 130, 238,1)',
                ],
              },
            ],
          }}
          height={550}
          width={600}
        />
      </div>
    );
  }
}

export default BoroChart;
