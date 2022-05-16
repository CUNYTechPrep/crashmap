// import React, { useEffect, useState } from 'react';
// import { Bar } from 'react-chartjs-2';
// import { Chart as ChartJS, BarElement } from 'chart.js';

// ChartJS.register(BarElement);

// function BarChart(props) {
//   const [chart, setChart] = useState({});

//   const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;

//   useEffect(() => {
//     const fetchData = async () => {
//       await fetch(`${api_prefix}boro_summary.json`)
//         .then((response) => {
//           if (response.ok) {
//             response.json().then((data) => {
//               // console.log(json.data);
//               setChart(data);
//             });
//           }
//         })
//         .catch((error) => {
//           console.log(error);
//         });
//     };
//     fetchData();
//   }, [api_prefix]);

//   console.log('chart', chart);
//   var data = {
//     labels: ['Manhattan', 'Bronx', 'Brooklyn', 'Queens', 'Staten Island'],
//     datasets: [
//       {
//         label: 'Collisions',
//         data: chart?.map((x) => x.collisions),
//         // data: [1, 2, 3, 4, 5],
//         backgroundColor: [
//           'rgba(100,178,71,0.2)', //MN
//           'rgba(192,120,98, 0.2)', //BX
//           'rgba(98,	123, 193, 0.2)', //BK
//           'rgba(192, 98, 170, 0.2)', //QN
//           'rgba(192, 167,	98, 0.2)', //SI
//         ],
//         borderColor: [
//           'rgba(100,178,71, 1)',
//           'rgba(192,120,98, 1)',
//           'rgba(98,	123, 193, 1)',
//           'rgba(192, 98, 170, 1)',
//           'rgba(192, 167,	98, 1)',
//         ],
//         borderWidth: 1,
//       },
//     ],
//   };
//   // render() {
//   return (
//     <div>
//       <Bar
//         data={data}
//         height={400}
//         width={600}
//         options={{
//           maintainAspectRatio: false,
//         }}
//       />
//       {/* <div>{this.state.chart}</div> */}
//     </div>
//   );
//   // }
// }

// export default BarChart;

// import React, { useState, useEffect } from 'react';
// import { Chart as ChartJS, BarElement } from 'chart.js';

// import { Bar } from 'react-chartjs-2';

// // ChartJS.register(BarElement);

// function BarChart() {
//   // const [chart, setChart] = useState({});
//   // // var baseUrl = "https://api.coinranking.com/v2/coins/?limit=10";
//   // // var proxyUrl = "https://cors-anywhere.herokuapp.com/";
//   // // var apiKey = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";

//   // const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;

//   // useEffect(() => {
//   //   const fetchData = async () => {
//   //     await fetch(`${api_prefix}boro_summary.json`)
//   //       .then((res) => {
//   //         res.json();
//   //         // if (response.ok) {
//   //         //   response.json().then((json) => {
//   //         //     console.log('here');
//   //         //     // setChart(json);
//   //         //   });
//   //         // }
//   //       })
//   //       .then((data) => console.log(data))
//   //       .catch((error) => {
//   //         console.log(error);
//   //       });
//   //   };
//   //   fetchData();
//   // }, [api_prefix]);

//   // console.log('chart', chart);
//   // var data = {
//   //   labels: ['Manhattan', 'Bronx', 'Brooklyn', 'Queens', 'Staten Island'],
//   //   datasets: [
//   //     {
//   //       label: 'Collisions',
//   //       // data: chart?.map((x) => x.collisions),
//   //       data: [1, 2, 3, 4, 5],
//   //       backgroundColor: [
//   //         'rgba(100,178,71,0.2)', //MN
//   //         'rgba(192,120,98, 0.2)', //BX
//   //         'rgba(98,	123, 193, 0.2)', //BK
//   //         'rgba(192, 98, 170, 0.2)', //QN
//   //         'rgba(192, 167,	98, 0.2)', //SI
//   //       ],
//   //       borderColor: [
//   //         'rgba(100,178,71, 1)',
//   //         'rgba(192,120,98, 1)',
//   //         'rgba(98,	123, 193, 1)',
//   //         'rgba(192, 98, 170, 1)',
//   //         'rgba(192, 167,	98, 1)',
//   //       ],
//   //       borderWidth: 1,
//   //     },
//   //   ],
//   // };

//   return (
//     <div>
//       <Bar
//         data={{
//           labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
//           datasets: [
//             {
//               label: '# of votes',
//               data: [12, 19, 3, 5, 2, 3],
//               backgroundColor: [
//                 'rgba(255, 99, 132, 0.2)',
//                 'rgba(54, 162, 235, 0.2)',
//                 'rgba(255, 206, 86, 0.2)',
//                 'rgba(75, 192, 192, 0.2)',
//                 'rgba(153, 102, 255, 0.2)',
//                 'rgba(255, 159, 64, 0.2)',
//               ],
//               borderColor: [
//                 'rgba(255, 99, 132, 1)',
//                 'rgba(54, 162, 235, 1)',
//                 'rgba(255, 206, 86, 1)',
//                 'rgba(75, 192, 192, 1)',
//                 'rgba(153, 102, 255, 1)',
//                 'rgba(255, 159, 64, 1)',
//               ],
//               borderWidth: 1,
//             },
//           ],
//         }}
//         height={400}
//         width={600}
//         options={{
//           maintainAspectRatio: false,
//         }}
//       />
//     </div>
//   );
// }

// export default BarChart;

import React, { useState, useEffect } from "react";
import { Bar } from "react-chartjs-2";
import Chart from "chart.js/auto";

const BarChart = (props) => {
  const [chart, setChart] = useState({});
  // const [selectedBorough, setBorough] = useState('');

  const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;

  useEffect(() => {
    if (props.selectedBorough == null) {
      const fetchData = async () => {
        await fetch(`${api_prefix}boro_summary.json`).then((res) => {
          res.json().then((data) => {
            setChart(data);
          });
        });
        // .catch((error) => {
        //   console.log(error);
        // });
      };
      fetchData();
      // console.log('inside fetch', props.selectedBorough);
    } else {
      switch (props.selectedBorough.value) {
        case 2:
          console.log("switch case bronx");
          break;
        case 3:
          console.log("switch case brooklyn");
          break;
        case 1:
          console.log("switch case manhattan");
          break;
        case 4:
          console.log("switch case queens");
          break;
        case 5:
          console.log("switch case staten island");
          break;
        default:
          console.log("nothin here!");
      }
    }
  }, [api_prefix, props]);

  console.log("chart: ", chart);
  // console.log('borough', selectedBorough);

  var data = {
    labels: ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"],
    datasets: [
      {
        label: "Collisions",
        // data: chart?.map((x) => x.collisions),
        data: [1, 2, 3, 4, 5],
        backgroundColor: [
          "rgba(100,178,71,0.2)", //MN
          "rgba(192,120,98, 0.2)", //BX
          "rgba(98,	123, 193, 0.2)", //BK
          "rgba(192, 98, 170, 0.2)", //QN
          "rgba(192, 167,	98, 0.2)", //SI
        ],
        borderColor: [
          "rgba(100,178,71, 1)",
          "rgba(192,120,98, 1)",
          "rgba(98,	123, 193, 1)",
          "rgba(192, 98, 170, 1)",
          "rgba(192, 167,	98, 1)",
        ],
        borderWidth: 1,
      },
    ],
  };
  return (
      <div>
        <Bar
            data={data}
            height={300}
            width={600}
            options={{
              maintainAspectRatio: false,
            }}
        />
      </div>
  );
};

export default BarChart;
