import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Search, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import { getGraphData } from '../services/api';
import { GraphData } from '../types';

const KnowledgeGraph = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [filter, setFilter] = useState('');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadGraphData();
  }, []);

  useEffect(() => {
    if (graphData.nodes.length > 0) {
      renderGraph();
    }
  }, [graphData, filter]);

  const loadGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getGraphData();
      setGraphData(data);
      if (data.nodes.length === 0) {
        setError('No graph data available. Upload documents to generate knowledge graph.');
      }
    } catch (err) {
      setError('Failed to load graph data. Please try again.');
      console.error('Graph load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderGraph = () => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    // Filter data
    const filteredNodes = graphData.nodes.filter(node =>
      node.label.toLowerCase().includes(filter.toLowerCase())
    );
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = graphData.edges.filter(
      edge => filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target)
    );

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    const g = svg.append('g');

    // Create force simulation
    const simulation = d3.forceSimulation(filteredNodes as any)
      .force('link', d3.forceLink(filteredEdges)
        .id((d: any) => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Draw edges
    const link = g.append('g')
      .selectAll('line')
      .data(filteredEdges)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Draw edge labels
    const edgeLabels = g.append('g')
      .selectAll('text')
      .data(filteredEdges)
      .enter()
      .append('text')
      .attr('font-size', 10)
      .attr('fill', '#666')
      .text(d => d.relation);

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(filteredNodes)
      .enter()
      .append('circle')
      .attr('r', 20)
      .attr('fill', d => d.id === selectedNode ? '#3b82f6' : '#60a5fa')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any);

    // Node labels
    const labels = g.append('g')
      .selectAll('text')
      .data(filteredNodes)
      .enter()
      .append('text')
      .text(d => d.label)
      .attr('font-size', 12)
      .attr('dx', 25)
      .attr('dy', 5)
      .style('pointer-events', 'none');

    // Node click handler
    node.on('click', (_event, d: any) => {
      setSelectedNode(d.id);
    });

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      edgeLabels
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      labels
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  };

  const handleZoomIn = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 1.3);
  };

  const handleZoomOut = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(d3.zoom<SVGSVGElement, unknown>().scaleBy as any, 0.7);
  };

  const handleReset = () => {
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().transform as any,
      d3.zoomIdentity
    );
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">Knowledge Graph Explorer</h1>
        <div className="flex gap-2">
          <button onClick={loadGraphData} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Refresh
          </button>
          <button onClick={handleZoomIn} className="p-2 bg-white rounded-lg shadow hover:bg-gray-50">
            <ZoomIn className="w-5 h-5" />
          </button>
          <button onClick={handleZoomOut} className="p-2 bg-white rounded-lg shadow hover:bg-gray-50">
            <ZoomOut className="w-5 h-5" />
          </button>
          <button onClick={handleReset} className="p-2 bg-white rounded-lg shadow hover:bg-gray-50">
            <Maximize2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Filter nodes..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
      </div>

      <div className="flex-1 bg-white rounded-lg shadow overflow-hidden relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading knowledge graph...</p>
            </div>
          </div>
        ) : error ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center p-8">
              <p className="text-red-600 mb-4">{error}</p>
              <button onClick={loadGraphData} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Retry
              </button>
            </div>
          </div>
        ) : graphData.nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center p-8">
              <p className="text-gray-600 mb-2">No knowledge graph data available.</p>
              <p className="text-sm text-gray-500">Upload documents to automatically generate the knowledge graph.</p>
            </div>
          </div>
        ) : (
          <svg ref={svgRef} className="w-full h-full" />
        )}
      </div>

      {selectedNode && (
        <div className="mt-4 bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">Selected Node: {selectedNode}</h3>
          <div className="text-sm text-gray-600">
            <p>Connections: {graphData.edges.filter(e => e.source === selectedNode || e.target === selectedNode).length}</p>
          </div>
        </div>
      )}

      <div className="mt-4 bg-blue-50 p-4 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Tips:</strong> Drag nodes to reposition • Scroll to zoom • Click nodes to select • Use search to filter
        </p>
      </div>
    </div>
  );
};

export default KnowledgeGraph;
