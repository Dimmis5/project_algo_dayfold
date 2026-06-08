import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, Play } from 'lucide-react';

const Complexity = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [nMax] = useState(5000);
    const [steps] = useState(10);
    const [algo, setAlgo] = useState('bfs');

    const algoInfo = {
        bfs: {
            name: "BFS (Friend Suggestions)",
            complexity: "O(N + E)",
            description: "BFS traverses each node and each edge once to find second-degree friends.",
            endpoint: "bfs",
            defaultN: 5000,
            minN: 100,
            color: "#ef4444" 
        },
        tree: {
            name: "Category Tree (Search)",
            complexity: "O(N)",
            description: "Recursive search in the category tree (Worst case: full traversal).",
            endpoint: "tree",
            defaultN: 5000,
            minN: 100,
            color: "#3b82f6" 
        },
        louvain: {
            name: "Louvain (Communities)",
            complexity: "O(N log N)",
            description: "Heuristic algorithm for community detection based on modularity.",
            endpoint: "louvain",
            defaultN: 5000,
            minN: 50,
            color: "#10b981" 
        },
        ppr: {
            name: "Personalized PageRank",
            complexity: "O(I * (N + E))",
            description: "Iterative calculation of importance scores relative to a source node (I = itérations).",
            endpoint: "ppr",
            defaultN: 5000,
            minN: 50,
            color: "#f59e0b" 
        },
        all: {
            name: "All Algorithms",
            complexity: "Comparison",
            description: "Comparison of real execution times of all algorithms on a single chart.",
            endpoint: "all",
            defaultN: 5000,
            minN: 100
        }
    };

    const runBenchmark = useCallback(async () => {
        setLoading(true);
        try {
            if (algo === 'all') {
                const endpoints = Object.keys(algoInfo).filter(k => k !== 'all');
                const fetchPromises = endpoints.map(k => 
                    fetch(`http://localhost:8000/complexity/benchmark/${algoInfo[k].endpoint}?n_max=${nMax}&steps=${steps}`)
                        .then(res => res.json())
                        .then(data => ({ key: k, data }))
                );
                
                const results = await Promise.all(fetchPromises);
                
                const mergedDataMap = new Map();
                results.forEach(({ key, data }) => {
                    data.forEach(item => {
                        if (!mergedDataMap.has(item.n)) {
                            mergedDataMap.set(item.n, { n: item.n });
                        }
                        const existing = mergedDataMap.get(item.n);
                        existing[`time_${key}`] = item.time;
                    });
                });
                
                const mergedData = Array.from(mergedDataMap.values()).sort((a, b) => a.n - b.n);
                setData(mergedData);

            } else {
                const response = await fetch(`http://localhost:8000/complexity/benchmark/${algoInfo[algo].endpoint}?n_max=${nMax}&steps=${steps}`);
                const result = await response.json();
                setData(result);
            }
        } catch (error) {
            console.error("Error fetching benchmark data:", error);
        } finally {
            setLoading(false);
        }
    }, [algo, nMax, steps]);

    useEffect(() => {
        runBenchmark();
    }, [runBenchmark]);

    const handleAlgoChange = (newAlgo) => {
        setAlgo(newAlgo);
        setData([]);
    };

    const renderChartLines = () => {
        if (algo === 'all') {
            return Object.keys(algoInfo)
                .filter(k => k !== 'all')
                .map(k => (
                    <Line 
                        key={k}
                        type="monotone" 
                        dataKey={`time_${k}`} 
                        stroke={algoInfo[k].color} 
                        strokeWidth={3}
                        dot={{ r: 3, fill: algoInfo[k].color }}
                        activeDot={{ r: 6 }}
                        name={algoInfo[k].name}
                        animationDuration={1000}
                        connectNulls
                    />
                ));
        } else {
            return [
                <Line 
                    key="time"
                    type="monotone" 
                    dataKey="time" 
                    stroke={algoInfo[algo].color || "#ef4444"} 
                    strokeWidth={3}
                    dot={{ r: 4, fill: algoInfo[algo].color || "#ef4444" }}
                    activeDot={{ r: 8 }}
                    name="Real Time"
                    animationDuration={1000}
                />,
                <Line 
                    key="theoretical"
                    type="monotone" 
                    dataKey="theoretical" 
                    stroke="#9ca3af" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    name={`Theoretical ${algoInfo[algo].complexity}`}
                    animationDuration={1000}
                />
            ];
        }
    };

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            <div className="max-w-6xl mx-auto">
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
                            <Activity className="text-red-500" />
                            Complexity Analysis
                        </h1>
                        <p className="text-gray-600 mt-2">Performance measurement for: <span className="font-semibold text-red-500">{algoInfo[algo].name}</span></p>
                    </div>
                    
                    <div className="flex flex-wrap gap-4 items-end">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Algorithm</label>
                            <select 
                                value={algo}
                                onChange={(e) => handleAlgoChange(e.target.value)}
                                className="mt-1 block w-48 border border-gray-300 rounded-md shadow-sm p-2 bg-white"
                            >
                                <option value="bfs">BFS Suggest Friends</option>
                                <option value="tree">Category Tree Search</option>
                                <option value="louvain">Louvain Communities</option>
                                <option value="ppr">Personalized PageRank</option>
                                <option value="all" className="font-bold">Compare All</option>
                            </select>
                        </div>

                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-lg">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-700">Time Performance</h2>
                        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
                            {algo === 'all' ? (
                                Object.keys(algoInfo).filter(k => k !== 'all').map(k => (
                                    <div key={k} className="flex items-center gap-2">
                                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: algoInfo[k].color }}></span>
                                        <span className="text-[10px] font-black text-gray-500 uppercase tracking-tighter">
                                            {algoInfo[k].name.split(' ')[0]}: <span className="text-gray-900">{algoInfo[k].complexity}</span>
                                        </span>
                                    </div>
                                ))
                            ) : (
                                <>
                                    <div className="flex items-center gap-2">
                                        <span className="w-3 h-3 rounded-full" style={{ backgroundColor: algoInfo[algo].color || "#ef4444" }}></span>
                                        <span className="text-sm text-gray-600 font-medium">Real (ms)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="w-3 h-3 rounded-full bg-gray-400"></span>
                                        <span className="text-sm text-gray-600 font-medium">Theoretical {algoInfo[algo].complexity}</span>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                    {data.length > 0 ? (
                        <div className="h-[500px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                                    <XAxis 
                                        dataKey="n" 
                                        label={{ value: 'Number of Nodes (N)', position: 'insideBottom', offset: -10 }} 
                                        tick={{fill: '#6b7280'}}
                                    />
                                    <YAxis 
                                        label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft', offset: 10 }}
                                        tick={{fill: '#6b7280'}}
                                    />
                                    <Tooltip 
                                        contentStyle={{ backgroundColor: '#fff', borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                    />
                                    <Legend />
                                    {renderChartLines()}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="h-[500px] flex items-center justify-center border-2 border-dashed border-gray-200 rounded-lg">
                            <p className="text-gray-400 italic">
                                {loading ? `Calculating complexity for ${algoInfo[algo].name}...` : "No data available."}
                            </p>
                        </div>
                    )}
                </div>

                <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">

                    </div>
                    </div>
                </div>
            
    );
};

export default Complexity;