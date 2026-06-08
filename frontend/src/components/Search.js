import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Search({ token }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const query = new URLSearchParams(useLocation().search).get('q');

  useEffect(() => {
    if (!query) return;

    const fetchResults = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/search?q=${query}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setResults(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query, token]);

  if (loading) return <div className="p-20 text-center text-gray-500 italic">Searching for "{query}"...</div>;

  return (
    <div className="max-w-[1600px] mx-auto px-2 md:px-8">
      <h2 className="text-xl font-bold mb-6 text-gray-700">
        {results.length} results for "{query}"
      </h2>

      {results.length === 0 ? (
        <div className="text-center py-20 bg-gray-50 rounded-[40px]">
          <p className="text-gray-400">No results found. Try "Art" or "Design".</p>
        </div>
      ) : (
        <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
          {results.map(pin => (
            <div key={pin.id} className="break-inside-avoid mb-4 group relative">
              <div className="relative rounded-[20px] overflow-hidden bg-gray-100 shadow-sm border border-gray-100">
                {pin.image_url ? (
                  <img 
                    src={pin.image_url.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`} 
                    className="w-full h-auto object-cover" 
                    alt={pin.title} 
                  />
                ) : (
                  <div className="w-full h-40 bg-gray-200 flex items-center justify-center text-gray-400 font-bold">
                    {pin.title[0]}
                  </div>
                )}
                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity p-3 flex flex-col justify-between">
                   <div className="flex justify-end">
                      <button className="bg-red-600 text-white px-4 py-2 rounded-full font-bold text-xs">Save</button>
                   </div>
                </div>
              </div>
              <p className="mt-2 text-sm font-semibold px-1">{pin.title}</p>
              <p className="text-[11px] text-gray-400 px-1 uppercase font-bold">{pin.category}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Search;
