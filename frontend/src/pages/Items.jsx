import React, { useEffect, useMemo, useState } from 'react';
import { useData } from '../state/DataContext';
import { Link } from 'react-router-dom';
import { FixedSizeList } from 'react-window';

const PAGE_SIZE = 50;
const ROW_HEIGHT = 40;
const LIST_HEIGHT = 420;

// Row renderer for react-window FixedSizeList
function Row({ index, style, data }) {
  const item = data[index];
  return (
    <div
      style={{
        ...style,
        display: 'flex',
        alignItems: 'center',
        padding: '0 8px',
        borderBottom: '1px solid #f2f2f2',
        boxSizing: 'border-box',
      }}
    >
      <Link to={'/items/' + item.id}>{item.name}</Link>
    </div>
  );
}

function Items() {
  const { items, total, loading, error, fetchItems } = useData();
  const [q, setQ] = useState('');
  const [page, setPage] = useState(1);

  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil((total || 0) / PAGE_SIZE));
  }, [total]);

  // AbortController prevents state updates after unmount (fixes memory leak)
  useEffect(() => {
    const controller = new AbortController();

    fetchItems({ q, page, pageSize: PAGE_SIZE, signal: controller.signal }).catch(err => {
      if (err?.name !== 'AbortError') console.error(err);
    });

    return () => controller.abort();
  }, [q, page, fetchItems]);

  // Clamp page if filtered results shrink totalPages
  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [page, totalPages]);

  if (loading && !items.length) return <p>Loading...</p>;

  return (
    <div style={{ padding: 16 }}>
      <label htmlFor="items-search">Search</label>
      <input
        id="items-search"
        value={q}
        onChange={e => {
          setQ(e.target.value);
          setPage(1);
        }}
        placeholder="Search items by name…"
        style={{ display: 'block', margin: '6px 0 12px', width: 300 }}
      />

      <div style={{ marginBottom: 12 }}>
        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
          Prev
        </button>
        <button
          onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
          style={{ marginLeft: 8 }}
        >
          Next
        </button>
        <span style={{ marginLeft: 12 }}>
          Page {page} / {totalPages} ({total} result{total === 1 ? '' : 's'})
        </span>
      </div>

      {error ? <p role="alert">Failed to load items.</p> : null}
      {!loading && !error && items.length === 0 ? <p>No results.</p> : null}

      {items.length ? (
        <div aria-busy={loading ? 'true' : 'false'}>
          {/* FixedSizeList is the correct react-window v1 API */}
          <FixedSizeList
            height={LIST_HEIGHT}
            itemCount={items.length}
            itemSize={ROW_HEIGHT}
            itemData={items}
            width="100%"
            style={{ border: '1px solid #eee' }}
          >
            {Row}
          </FixedSizeList>
        </div>
      ) : null}
    </div>
  );
}

export default Items;
