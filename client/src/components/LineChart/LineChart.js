import React, { Component } from "react";
import { Line } from "react-chartjs-2";
import moment from "moment";

class LineChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      data: null,
      options: null,
    };
  }
  componentDidMount() {
    const skipped = (ctx, value) =>
      ctx.p0.skip || ctx.p1.skip ? value : undefined;
    const down = (ctx, value) =>
      ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;

    const timeFormat = "YYYY-DD-MM";

    this.setState({
      data: {
        labels: [
          //   moment("2020-01-01"),
          //   moment("2020-01-02"),
          //   moment("2020-01-03"),
          //   moment("2020-01-04"),
          //   moment("2020-01-05"),
        ],
        datasets: [
          {
            label: "My First Dataset",
            data: [
              {
                x: "2020-01-01",
                y: 175,
              },
              {
                x: "2020-01-02",
                y: 175,
              },
              {
                x: NaN,
                y: NaN,
              },
              {
                x: "2020-01-03",
                y: 178,
              },
              {
                x: "2020-01-04",
                y: 178,
              },
            ],
            borderColor: "rgb(75, 192, 192)",
            segment: {
              borderColor: (ctx) =>
                skipped(ctx, "rgb(0,0,0,0.2)") || down(ctx, "rgb(192,75,75)"),
              borderDash: (ctx) => skipped(ctx, [6, 6]),
            },
            spanGaps: true,
          },
        ],
      },
      options: {
        scales: {
          x: {
            type: "time",
            time: {
              format: timeFormat,
              tooltipFormat: "ll",
            },
          },
        },
      },
    });
    this.setState({ isLoading: false });
  }

  render() {
    if (this.state.isLoading) {
      return null;
    }
    return <Line data={this.state.data} height={300} />;
  }
}

export default LineChart;
