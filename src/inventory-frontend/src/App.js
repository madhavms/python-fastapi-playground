import './App.css';
import { useEffect, useState } from 'react';
import { Loader } from './components/Loader';

function App() {

  useEffect(() => {
    async function getProductDetails(){
      const res = await fetch('http://localhost:8001/products')
      const data = await res.json()
      console.log(data)
      setProducts(data)
      setIsLoading(false)
    }

    getProductDetails()
    
  },[])

  const [products, setProducts] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  const sortByName = () => {
    console.log('clicked')
    setProducts(products.sort((a,b) => {
      let name1 = a.name
      let name2 = b.name
      console.log(a.name, typeof(a.name), typeof(b.name),a,b)
      return String(name1).localCompare(String(name2))
    }))
  }

  return (
    <div className="App">
    <Loader isLoading={isLoading}>
    {!!products.length && 
      <table>
      <tbody>
      <tr>
      <th onClick={sortByName}>Name</th>
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
    </Loader>
    </div>
  );
}

export default App;
