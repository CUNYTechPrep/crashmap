import React, { Component } from "react";
import Select from "react-select";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import "./styles.css";
import ListGroup from 'react-bootstrap/ListGroup'

const options = [
  { value: 2, label: 'Bronx', lng: '-73.865433', lat: '40.8448' },
  { value: 3, label: 'Brooklyn', lng: '-73.9442', lat: '40.6782' },
  { value: 4, label: 'Queens', lng: '-73.7949', lat: '40.7282' },
  { value: 1, label: 'Manhattan', lng: '-73.9712', lat: '40.7831' },
  {
    value: 5,
    label: 'Staten Island',
    lng: '-74.1502',
    lat: '40.5795',
  },
];
function Rank(props){
  return(
    <div>
           <ListGroup >
  <ListGroup.Item  variant='primary'>{props.name} : {props.total}</ListGroup.Item>
  

</ListGroup>
    </div>
  )
}
class Filter extends Component {
  constructor(props) {
    super(props);
    this.state ={
      boroughSummary: []
    }
  }

  componentDidMount(){
    const api_prefix = process.env.REACT_APP_API_PROXY_URL_PREFIX;
    console.log('yup')
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
                
             
                obj2.push(({id:'Manhattan', coll : obj[x].collision, boro_id : obj[x].id}))
                
                break;
              case 1:
            
                obj2.push({id:'Bronx', coll : obj[x].collision , boro_id : obj[x].id })
   
                break;
              case 2:
               
                obj2.push({id:'Brooklyn', coll : obj[x].collision , boro_id : obj[x].id})
     
                break;
              case 3:
                 
                  obj2.push({id:'Queens', coll : obj[x].collision , boro_id : obj[x].id})
         
                  break;
               case 4:
                  
                  obj2.push({id:'Staten Island', coll : obj[x].collision, boro_id : obj[x].id })

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
  }
  currentBorough = (event) => {
    if (this.props.selectedBorough)
      console.log("inside currentBorough: " + this.props.selectedBorough.value);
    else console.log("inside currentBorough: nothing selected!");
  };

  render() {
    return (
      <div>
        <div className='option border border-3 border-primary rounded  p-3 mb-3'>
          <div className='card row'>
            <ul className=' list-group list-group-flush'>
              <div className='col'></div>
      <li className='list-group-item' >
       <p>View Neighborhood Boundaries</p>
       <Select
            value={this.props.selectedBorough}
            onChange={this.props.handleBoroughChange}
            options={options}
          />
            <button className='btn btn-primary' onClick={this.currentBorough}>
            Enter city
          </button>
  
       
      </li>
      </ul>
     
      </div>
      
      </div>
      <div><h2>Ranking of most Collisions</h2>{this.state.boroughSummary.map((rank,i) => <Rank list={rank.boro_id}name={rank.id} total={rank.coll}></Rank>)}</div>
      </div>
    );
  }
}

export default Filter;
