import React from 'react';
import { Bar } from 'react-chartjs-2';
import Chart from 'chart.js/auto';

class BarChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      labels: ['Manhattan', 'Bronx', 'Brooklyn', 'Queens', 'Staten Island'],
      borough: [],
      visibility: 'show',
      // data: [],
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
          id: '1',
          collision: json[0].collisions,
          name: 'Manhattan',
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
          id: '2',
          collision: json[0].collisions,
          name: 'Bronx',
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
          id: '3',
          collision: json[0].collisions,
          name: 'Brooklyn',
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
          id: '4',
          collision: json[0].collisions,
          name: 'Queens',
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
          id: '5',
          collision: json[0].collisions,
          name: 'Staten Island',
        };
        arr2.push(arr3);

        this.setState({
          borough: arr2,
        });
      });
  }

  componentDidUpdate(prevProps) {
    // if (this.state.visibility === 'show') {
    //   this.setState({ visibility: 'hide' });
    // }
    if (
      this.props.selectedBorough !== null &&
      this.state.visibility === 'show'
    ) {
      this.setState({ visibility: 'hide' });
    }
  }

  render() {
    return (
      <div className={`${this.state.visibility}`}>
        <Bar
          //   data={this.state.data}
          data={{
            labels: [
              'Manhattan',
              'Bronx',
              'Brooklyn',
              'Queens',
              'Staten Island',
            ],
            datasets: [
              {
                label: 'Collisions',
                data: this.state.borough?.map((x) => x.collision),
                // data: [1, 2, 3, 4, 5],
                backgroundColor: [
                  'rgba(100,178,71,0.2)', //MN
                  'rgba(192,120,98, 0.2)', //BX
                  'rgba(98,	123, 193, 0.2)', //BK
                  'rgba(192, 98, 170, 0.2)', //QN
                  'rgba(192, 167,	98, 0.2)', //SI
                ],
                borderColor: [
                  'rgba(100,178,71, 1)',
                  'rgba(192,120,98, 1)',
                  'rgba(98,	123, 193, 1)',
                  'rgba(192, 98, 170, 1)',
                  'rgba(192, 167,	98, 1)',
                ],
                borderWidth: 1,
              },
            ],
          }}
          height={550}
          width={600}
          //   options={{
          //     maintainAspectRatio: false,
          //   }}
        />
      </div>
    );
  }
}

export default BarChart;
