import React, { Component } from "react";
import Card from "react-bootstrap/Card";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import { ListGroup, ListGroupItem } from "react-bootstrap";

const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;
let x;

function AllCity(props) {
  return (
    <div>
      <div className="container">
        <Row>
          <Col m={3}>
            <div className="card border border-dark rounded bg-dark text-light">
              <div className="card-body">
                <div className="card-title">Overview of Boroush</div>
                <p className="card-text">
                  inside of {props.hood} There has been a total of collisions{" "}
                  {props.collide}.
                </p>
              </div>
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
}

function Choice(props) {
  const isThereInfo = props.isThereInfo;
  if (isThereInfo) {
    return (
      <div>
        {props.borough.map((content) => (
          <Container fluid style={{ paddingLeft: 0, paddingRight: 0 }}>
            <Row>
              <Col
                p={4}
                style={{ paddingLeft: 0, paddingRight: 0, marginRight: 4 }}
              >
                {["Light"].map((variant) => (
                  <Card
                    className="text-center"
                    bg={variant.toLowerCase()}
                    text={variant.toLowerCase() === "light" ? "dark" : "white"}
                    style={{ height: "120px" }}
                  >
                    <Card.Body className="align-items-center d-flex flex-column justify-content-center h-100">
                      <Card.Text>Collisions</Card.Text>
                      <Card.Title key={content.keys}>
                        +{content.collisions}
                      </Card.Title>
                    </Card.Body>
                  </Card>
                ))}
              </Col>
              <Col
                p={4}
                style={{ paddingLeft: 0, paddingRight: 0, marginRight: 4 }}
              >
                {["Light"].map((variant) => (
                  <Card
                    className="text-center "
                    bg={variant.toLowerCase()}
                    text={variant.toLowerCase() === "light" ? "dark" : "white"}
                    style={{ height: "120px" }}
                  >
                    <Card.Body className="align-items-center d-flex flex-column justify-content-center h-100">
                      <Card.Text>Individuals</Card.Text>
                      <Card.Title>+{content.people}</Card.Title>
                    </Card.Body>
                  </Card>
                ))}
              </Col>
              <Col p={4} style={{ paddingLeft: 0, paddingRight: 0 }}>
                {["Light"].map((variant) => (
                  <Card
                    className="text-center "
                    bg={variant.toLowerCase()}
                    text={variant.toLowerCase() === "light" ? "dark" : "white"}
                    style={{ height: "120px" }}
                  >
                    <Card.Body className="align-items-center d-flex flex-column justify-content-center h-100">
                      <Card.Text>Vehicles</Card.Text>
                      <Card.Title>+{content.vehicles}</Card.Title>
                    </Card.Body>
                  </Card>
                ))}
              </Col>
            </Row>
          </Container>
        ))}
      </div>
    );
  } else {
    return <Before />;
  }
}

function Before(props) {
  return (
    <div>
      <Container fluid style={{ paddingLeft: 0, paddingRight: 0 }}>
        <Row>
          <Col
            p={4}
            style={{
              paddingLeft: 0,
              paddingRight: 0,
              marginRight: 4,
            }}
          >
            {["Light"].map((variant) => (
              <Card
                bg={variant.toLowerCase()}
                text={variant.toLowerCase() === "light" ? "dark" : "white"}
                style={{ height: "120px" }}
              >
                <Card.Title className="align-items-center d-flex justify-content-center h-100">
                  Click Borough
                </Card.Title>
              </Card>
            ))}
          </Col>
          <Col
            p={4}
            style={{ paddingLeft: 0, paddingRight: 0, marginRight: 4 }}
          >
            {["Light"].map((variant) => (
              <Card
                bg={variant.toLowerCase()}
                text={variant.toLowerCase() === "light" ? "dark" : "white"}
                style={{ height: "120px" }}
              >
                <Card.Title className="align-items-center d-flex justify-content-center h-100">
                  Click Borough
                </Card.Title>
              </Card>
            ))}
          </Col>
          <Col p={4} style={{ paddingLeft: 0, paddingRight: 0 }}>
            {["Light"].map((variant) => (
              <Card
                bg={variant.toLowerCase()}
                text={variant.toLowerCase() === "light" ? "dark" : "white"}
                style={{ height: "120px" }}
              >
                <Card.Title className="align-items-center d-flex justify-content-center h-100">
                  Click Borough
                </Card.Title>
              </Card>
            ))}
          </Col>
        </Row>
      </Container>
    </div>
  );
}
function Con(props) {
  return (
    <div>
      <Container>
        <Row>
          <Col>{/* <h1 className='text-center'>{props.selected}</h1> */}</Col>
        </Row>
        <Row>
          <Col m={6}>
            {" "}
            {["Light"].map((variant) => (
              <Card
                bg={variant.toLowerCase()}
                text={variant.toLowerCase() === "light" ? "dark" : "white"}
                style={{ width: "18rem" }}
              >
                <Card.Header>{props.many}</Card.Header>
                <Card.Body>
                  <Card.Title></Card.Title>
                  <Card.Text key={props.keys}>
                    From {props.start} through {props.end}, There has been a
                    total of collisions {props.crashes} involving{" "}
                    {props.vehicles} vehicles.
                  </Card.Text>
                </Card.Body>
              </Card>
            ))}
          </Col>
          <Col m={6}>
            {["Light"].map((variant) => (
              <Card
                bg={variant.toLowerCase()}
                text={variant.toLowerCase() === "light" ? "dark" : "white"}
                style={{ width: "18rem" }}
              >
                <Card.Body>
                  <Card.Title>{props.peoples}</Card.Title>
                  <Card.Text>
                    From {props.start} through {props.end}, There has been a
                    total of {props.people} involved. There was{" "}
                    {props.occupants} occupants, {props.cyclists} cyclists . For
                    more info Click a neighborhood!
                  </Card.Text>
                </Card.Body>
              </Card>
            ))}
          </Col>
        </Row>
      </Container>
    </div>
  );
}
let arr = [];
let arr2 = [];
class Overview extends Component {
  constructor(props) {
    super(props);
    this.state = {
      lng: -73.9066,
      lat: 40.7294,
      zoom: 9.5,
      borough: [],
      boroughSummary: [],
      currentNeighbor: [],
      NeighborCollision: [],
      selected: " ",
      peoples: "Click a borough",
      many: "Click a borough",
      isThereInfo: false,
    };
  }
  componentDidMount() {
    console.log(this.state.borough);
  }
  componentDidUpdate(prevProps) {
    if (prevProps.selectedBorough !== this.props.selectedBorough) {
      console.log(this.props.selectedBorough);
      console.log(this.props.selectedBorough.value);
      fetch(
        `${api_prefix}boro_summary.json?boro_id=${this.props.selectedBorough.value}&start_date=2020-01-01&end_date=2020-01-31`
      )
        .then(function (res) {
          return res.json();
        })
        .then((json) => {
          console.log(json);
          this.setState({
            borough: json,
            selected: `Overview of ${this.props.selectedBorough.label}`,
            peoples: "Who was involved?",
            many: "How many collisions?",
          });
        });

      fetch(
        `${api_prefix}nta2020.geojson?boro_id=${this.props.selectedBorough.value}`
      )
        .then(function (res) {
          return res.json();
        })
        .then((json) => {
          arr = [];
          console.log(json.features);
          json.features.map((summary) => arr.push(summary.properties));
          console.log(arr);
          arr2 = arr.map((summary) => ({
            id: summary.id,
            town: summary.name,
          }));
          console.log(arr2);

          console.log(json.features);
          this.setState({
            currentNeighbor: arr2,
            isThereInfo: true,
          });
          console.log(this.state.currentNeighbor);
        });

      // fetch(`${api_prefix}city_summary.json?start_date=2020-01-01&end_date=2020-01-31`)
      // .then(function(res){
      //   return res.json()
      // })
      // .then((json)=>{

      //     this.setState({
      //       boroughSummary:json
      //     })
      // })
      // if(this.state.currentNeighbor[2] !== undefined)
      // {
      //   console.log(this.state.currentNeighbor[2])
      //       // fetch(`${api_prefix}nta2020_summary.json?nta2020_id=${arr[i]}&start_date=2020-01-01&end_date=2020-01-31`)
      //           // .then(function(res){
      //           //   return res.json()
      //           // })
      //           // .then((json)=>{
      //           //   arr2.push(json)
      //           //   this.setState({
      //           //     boroughSummary:json
      //           //   })

      //           // })
      // }
      // else{
      //   console.log(this.state.currentNeighbor[2])
      // }
    }
  }

  render() {
    return (
      <div>
        <div>
          <Choice
            borough={this.state.borough}
            isThereInfo={this.state.isThereInfo}
            many={this.state.many}
            peoples={this.state.peoples}
            // currentb={this.props.selectedBorough.label}
          />
        </div>
        {/* <div className=''>
          {' '}
          {this.state.borough.map((content, i) => (
            <Con 
              key={content.keys}
              crashes={content.collisions}
              start={content.start_date}
              end={content.end_date}
              vehicles={content.vehicles}
              keys={content.key}
              selected={this.state.selected}
              peoples={this.state.peoples}
              people={content.people}
              cyclists={content.cyclists}
              occupants={content.occupants}
              many={this.state.many}
            />
          ))}{' '}
        </div> */}
        {/* <div className=''>{this.state.currentNeighbor.map((info,i)=> <AllCity collide={info.id } hood={info.town}
              ></AllCity>)}</div> */}
      </div>
    );
  }
}

export default Overview;
