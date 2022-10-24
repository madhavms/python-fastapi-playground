import logo from './logo.svg';
import './App.css';
import { useEffect } from 'react';

function App() {

  useEffect(() => {
    async function getProductDetails(){
      const data = await fetch('http://localhost:8001/products')
      console.log(data)
    }

    getProductDetails()
    
  },[])



  return (
    <div className="App">
      
    </div>
  );
}

export default App;
