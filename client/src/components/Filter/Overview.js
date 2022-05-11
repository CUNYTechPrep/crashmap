import React, { Component } from 'react';
import Card from 'react-bootstrap/Card'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import ListGroup from 'react-bootstrap/ListGroup'



const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;
let x;

function AllCity(props){
  return(
    <div>
      <div className='container'>
      <Row>
        <Col m={3}>
        <div className="card border border-dark rounded bg-dark text-light" >
        <div className="card-body">
        <div className="card-title">
          Overview of Boroush
        </div>
        <p className="card-text">inside of {props.hood} There has been a total of collisions {props.collide}.</p>
          
        </div>
  
      </div>
      </Col>
      
      </Row>
      </div>
    </div>
  )
}
function Rank(props){
  return(
    <div>
           <ListGroup>
  <ListGroup.Item variant='primary'>{props.name} : {props.total}</ListGroup.Item>

</ListGroup>
    </div>
  )
}
function Con(props) {


  return (
    <div>
      <Container >
        <Row>
          <Col><h1 className='text-center'>Overview of {props.currentb}</h1>
          </Col>
        </Row>
        <Row>
        <Col m={3}>      {[
    'Primary',
    // 'Secondary',
    // 'Success',
    // 'Danger',
    // 'Warning',
    // 'Info',
    // 'Light',
    // 'Dark',
  ].map((variant) => (
      <Card 
        bg={variant.toLowerCase()}
        text={variant.toLowerCase() === 'light' ? 'dark' : 'white'}
      
      style={{width:'18rem'}}>
        <Card.Body>
          <Card.Title>
          How many collisions?
          </Card.Title>
          <Card.Text>
          From {props.start} through {props.end}, There has been a total of collisions {props.crashes} involving {props.vehicles} vehicles.
          </Card.Text>
        </Card.Body>

      </Card>
      ))}</Col>
        <Col m={3}> 
        {[
    // 'Primary',
    // 'Secondary',
    // 'Success',
    'Danger',
    // 'Warning',
    // 'Info',
    // 'Light',
    // 'Dark',
  ].map((variant) => (
        <Card     bg={variant.toLowerCase()}
        text={variant.toLowerCase() === 'light' ? 'dark' : 'white'}
     
      style={{width:'18rem'}}>
        <Card.Body>
          <Card.Title>
          Who were the people involved?
          </Card.Title>
          <Card.Text>
          From {props.start} through {props.end}, There has been a total of {props.people} involved. There was {props.occupants} occupants, {props.cyclists} cyclists . For more info Click a neighborhood!
          </Card.Text>
        </Card.Body>

      </Card>
  ))}</Col>
 
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
          NeighborCollision:[],
    
        };
    }
 
  componentDidUpdate(prevProps){
  
    if (prevProps.selectedBorough !== this.props.selectedBorough) {

        console.log(this.props.selectedBorough)
        console.log(this.props.selectedBorough.label)
        fetch(`${api_prefix}boro_summary.json?boro_id=${this.props.selectedBorough.value}&start_date=2020-01-01&end_date=2020-01-31`)
        .then(function(res){
          return res.json()
        })
        .then((json) =>{
          console.log(json)
          this.setState({
            borough:json
          });
              
        })
        fetch(`${api_prefix}boro_summary.json?start_date=2020-01-01&end_date=2020-01-31`)
        .then(function(res){
          return res.json()
        })
        .then((json) =>{
          console.log(json)
          let obj = json.map(sum =>({id:sum.boro_id,collision:sum.collisions}))
         console.log(obj)
         let obj2 = [];
   
          for(let x = 0; x< obj.length; x++)
          {
            
            
            switch(x){
              case 0:
                
             
                obj2.push(({id:'Manhattan', coll : obj[x].collision }))
                
                break;
              case 1:
            
                obj2.push({id:'Bronx', coll : obj[x].collision })
   
                break;
              case 2:
               
                obj2.push({id:'Brooklyn', coll : obj[x].collision })
     
                break;
              case 3:
                 
                  obj2.push({id:'Queens', coll : obj[x].collision })
         
                  break;
               case 4:
                  
                  obj2.push({id:'Staten Island', coll : obj[x].collision })

                  break;
              default:
                console.log('not it!')
            }
           
          }
          obj2.sort((a,b)=>{
            if (a.coll < b.coll)
            {
              return 1
            }
            else{
              return -1
            }
          })
          console.log(obj2)
          this.setState({
            boroughSummary:obj2
          })
   
        })
        fetch(`${api_prefix}nta2020.geojson?boro_id=${this.props.selectedBorough.value}`)
        .then(function(res){
          return res.json()
        })
        .then((json)=>{
          arr = []
      
          json.features.map(summary => arr.push(summary.id))
         arr2 = json.features.map(summary => (
             
          {id: summary.id, town:summary.name}))
         console.log(arr2)
          console.log(arr)
          console.log(json.features)
          this.setState({
            currentNeighbor:arr2
          })
          console.log(this.state.currentNeighbor) 
        })
      
       
         
        
  
        
   

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
            <div>{this.state.boroughSummary.map((rank,i) => <Rank name={rank.id} total={rank.coll}></Rank>)}</div>
               <div className=''> {this.state.borough.map((content, i) => <Con crashes={content.collisions}  start={content.start_date} end={content.end_date}
        vehicles={content.vehicles} keys={content.key}  currentb={this.props.selectedBorough.label} 
        people={content.people} cyclists={content.cyclists} occupants={content.occupants}  />)} </div>
              {/* <div className=''>{this.state.currentNeighbor.map((info,i)=> <AllCity collide={info.id } hood={info.town}
              ></AllCity>)}</div> */}
        </div>
      );
    }
  }
  
  export default Overview;
  