import Map from "./components/Map/Map.js";
import Filter from "./components/Filter/Filter.js";
import { Container } from "react-bootstrap";

import "./App.css";

function App() {
  return (
    <Container className="mt-5">
      <div id="hero">
        <Filter />
        <Map />
      </div>
    </Container>
  );
}

export default App;
