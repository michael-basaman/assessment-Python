import React, { createContext, useCallback, useContext, useState } from 'react';

const DataContext = createContext();

export function DataProvider({ children }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchItems = useCallback(async ({ q = '', page = 1, pageSize = 50, signal } = {}) => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    params.set('page', String(page));
    params.set('pageSize', String(pageSize));

    try {
      const res = await fetch(`/api/items?${params.toString()}`, { signal });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);

      const json = await res.json();

      const nextItems = Array.isArray(json) ? json : json.items;
      const nextTotal = typeof json?.total === 'number' ? json.total : nextItems.length;

      setItems(nextItems);
      setTotal(nextTotal);

      return json;
    } catch (err) {
      if (err?.name !== 'AbortError') setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <DataContext.Provider value={{ items, total, loading, error, fetchItems }}>
      {children}
    </DataContext.Provider>
  );
}

export const useData = () => useContext(DataContext);
