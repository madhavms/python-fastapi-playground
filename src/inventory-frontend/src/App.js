import './App.css';
import { useEffect, useState } from 'react';

function App() {

  useEffect(() => {
    async function getProductDetails(){
      const res = await fetch('http://localhost:8001/products')
      const data = await res.json()
      console.log(data)
      setProducts(data)
    }

    getProductDetails()
    
  },[])

  const [products, setProducts] = useState([])

  return (
    <div className="App">
    {!!products.length && 
      <table>
      <tbody>
      <tr>
      <th>Name</th>
      <th>Price</th>
      <th>Quantity</th>
      </tr>
      {products.map(
        product => (
          <tr key={product.id}>
          <td>{product.name}</td>
          <td>{product.price}</td>
          <td>{product.quantity}</td>
          </tr>
        )
      )}
      </tbody>
      </table>
    }
    </div>
  );
}

export default App;
