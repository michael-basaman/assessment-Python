import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function ItemDetail() {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // AbortController prevents memory leak if component unmounts before fetch completes
    const controller = new AbortController();

    fetch('/api/items/' + id, { signal: controller.signal })
      .then(res => res.ok ? res.json() : Promise.reject(res))
      .then(setItem)
      .catch(err => {
        if (err?.name !== 'AbortError') navigate('/');
      });

    return () => controller.abort();
  }, [id, navigate]);

  if (!item) return <p>Loading...</p>;

  return (
    <div style={{ padding: 16 }}>
      <h2>{item.name}</h2>
      <p><strong>Category:</strong> {item.category}</p>
      <p><strong>Price:</strong> ${item.price}</p>
    </div>
  );
}

export default ItemDetail;