"""
Enterprise Emergency Network Simulator

A professional-grade interactive tool for simulating and analyzing emergency
network topology using advanced graph algorithms and real-time analytics.
Version: 3.1.0 (Fixed & Optimized)
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List, Dict, Tuple, Callable
from dataclasses import dataclass
import threading
import time
import queue
import random

import matplotlib
matplotlib.use("TkAgg")  # Must be called before importing pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ApplicationConfig:
    """Application configuration constants."""
    WINDOW_TITLE = "Enterprise Emergency Network Simulator v3.1"
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    FIGURE_WIDTH = 8
    FIGURE_HEIGHT = 7
    
    NODE_COUNT = 8
    NODE_SIZE = 700
    FIGURE_SEED = 42
    
    COLOR_MAP = {
        0: "red", 1: "blue", 2: "green", 3: "yellow",
        4: "orange", 5: "purple", 6: "pink", 7: "brown"
    }
    HIGHLIGHT_COLOR = "red"
    NODE_DEFAULT_COLOR = "lightblue"
    EDGE_DEFAULT_COLOR = "gray"
    HIGHLIGHT_WIDTH = 3


@dataclass
class NetworkMetrics:
    """Container for network performance metrics."""
    density: float
    avg_clustering: float
    avg_path_length: float
    diameter: float
    connected_components: int
    avg_degree: float


class LoadingDialog(tk.Toplevel):
    """Animated loading dialog with spinner."""
    
    def __init__(self, parent, title="Processing"):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")
        
        # UI elements
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.label = ttk.Label(frame, text="Processing...", font=("Arial", 12, "bold"))
        self.label.pack(pady=10)
        
        self.progress = ttk.Progressbar(frame, mode='indeterminate', length=250)
        self.progress.pack(pady=10)
        self.progress.start()
        
        self.spinner_chars = ['|', '/', '-', '\\']
        self.current_spinner = 0
        self.animate()
    
    def animate(self):
        """Update spinner animation."""
        try:
            if not self.winfo_exists():
                return
            spinner = self.spinner_chars[self.current_spinner % len(self.spinner_chars)]
            self.label.config(text=f"{spinner} Processing...")
            self.current_spinner += 1
            self.after(200, self.animate)
        except tk.TclError:
            pass


class ResultPage(ttk.Frame):
    """Dedicated result display page."""
    
    def __init__(self, parent, title, result_data, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback
        
        # Header with title and buttons
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(header, text="< Back", command=self._on_back).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text=title, font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=20)
        
        # Action buttons
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Copy Text", command=self._copy_text).pack(side=tk.LEFT, padx=5)
        
        # Result text display
        self.text_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Courier", 10))
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.display_result(result_data)
    
    def display_result(self, text):
        """Display result text."""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.END, text)
        self.text_display.config(state=tk.DISABLED)
    
    def _copy_text(self):
        """Copy text to clipboard."""
        text = self.text_display.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Results copied to clipboard.")
    
    def _on_back(self):
        """Go back to previous view."""
        if self.on_back_callback:
            self.on_back_callback()


class EmergencyNetworkSimulator(tk.Tk):
    """
    Enterprise Emergency Network Simulator with advanced analytics.
    """
    
    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__()
        
        self.title(ApplicationConfig.WINDOW_TITLE)
        self.geometry(f"{ApplicationConfig.WINDOW_WIDTH}x{ApplicationConfig.WINDOW_HEIGHT}")
        self.minsize(1200, 700)
        
        # Initialize state
        self.G: nx.Graph = nx.Graph()
        self.G_original: nx.Graph = nx.Graph()
        self.metrics: Optional[NetworkMetrics] = None
        self.selected_algorithm: tk.StringVar = tk.StringVar(value="mst")
        self.result_queue: queue.Queue = queue.Queue()
        
        # Main container for switching between views
        self.container = ttk.Frame(self)
        self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.current_frame = None
        
        # Initialize components
        self._initialize_graph()
        self._create_dashboard()
        self._calculate_metrics()
        self._display_analytics()
        self._draw_graph()
        
        # Start queue checker
        self._check_queue()
        
        logger.info("Enterprise Network Simulator initialized successfully")

    def _initialize_graph(self) -> None:
        """Initialize the sample network graph with nodes and weighted edges."""
        try:
            # Add nodes with attributes
            for i in range(1, ApplicationConfig.NODE_COUNT + 1):
                self.G.add_node(i, status="active", load=0.5)
            
            # Define edges with weights and capacities
            edges: List[Tuple[int, int, int, int]] = [
                (1, 2, 4, 100), (1, 3, 3, 100), (2, 4, 5, 80),
                (3, 4, 6, 60), (3, 5, 2, 120), (5, 6, 4, 90),
                (6, 7, 3, 110), (7, 8, 2, 100), (4, 8, 7, 50)
            ]
            
            for u, v, w, cap in edges:
                self.G.add_edge(u, v, weight=w, capacity=cap, utilization=0.3)
            
            # Create backup for reset
            self.G_original = self.G.copy()
            
        except Exception as e:
            logger.error(f"Failed to initialize graph: {e}")
            raise

    def _calculate_metrics(self) -> None:
        """Calculate comprehensive network metrics."""
        try:
            if not self.G.nodes():
                return
            
            density = nx.density(self.G)
            avg_clustering = nx.average_clustering(self.G) if len(self.G) > 2 else 0
            
            if nx.is_connected(self.G):
                avg_path_length = nx.average_shortest_path_length(self.G)
                diameter = nx.diameter(self.G)
            else:
                avg_path_length = float('inf')
                diameter = float('inf')
            
            connected_components = nx.number_connected_components(self.G)
            degrees = [d for n, d in self.G.degree()]
            avg_degree = np.mean(degrees) if degrees else 0
            
            self.metrics = NetworkMetrics(
                density=density,
                avg_clustering=avg_clustering,
                avg_path_length=avg_path_length,
                diameter=diameter,
                connected_components=connected_components,
                avg_degree=avg_degree
            )
            
        except Exception as e:
            logger.warning(f"Could not calculate all metrics: {e}")
            self.metrics = None

    def _create_dashboard(self) -> None:
        """Create main dashboard with tabbed interface."""
        try:
            # Main dashboard frame
            main_frame = ttk.Frame(self.container)
            main_frame.grid(row=0, column=0, sticky="nsew")
            self.frames['dashboard'] = main_frame
            
            main_frame.grid_rowconfigure(0, weight=1)
            main_frame.grid_columnconfigure(0, weight=1)
            
            # Create notebook (tabbed interface)
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # Tab 1: Visualization
            self._create_visualization_tab()
            
            # Tab 2: Analytics
            self._create_analytics_tab()
            
            # Tab 3: Algorithm Suite
            self._create_algorithm_tab()
            
            self._show_frame('dashboard')
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    def _create_visualization_tab(self) -> None:
        """Create graph visualization tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Visualization")
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(tab, text="Network Controls", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self._add_button(control_frame, "Reset Network", self._on_reset_network)
        self._add_button(control_frame, "Calculate MST", self._on_generate_mst)
        self._add_button(control_frame, "Find Disjoint Paths", self._on_show_paths)
        self._add_button(control_frame, "Simulate Failure", self._on_simulate_failure)
        self._add_button(control_frame, "Optimize Tree", self._on_optimize_tree)
        self._add_button(control_frame, "Graph Coloring", self._on_graph_coloring)
        self._add_button(control_frame, "Centrality Analysis", self._on_centrality_analysis)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Right panel - Graph canvas
        canvas_frame = ttk.LabelFrame(tab, text="Network Topology", padding=5)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure 



        self.fig = Figure(figsize=(ApplicationConfig.FIGURE_WIDTH, ApplicationConfig.FIGURE_HEIGHT), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_analytics_tab(self) -> None:
        """Create network analytics dashboard."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Analytics")
        
        # Metrics display
        metrics_frame = ttk.LabelFrame(tab, text="Network Metrics", padding=10)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame, height=15, width=80, font=("Courier", 10)
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        self.metrics_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        self._add_button(button_frame, "Refresh Metrics", self._on_refresh_analytics)

    def _create_algorithm_tab(self) -> None:
        """Create algorithm selection and execution tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Algorithm Suite")
        
        algo_frame = ttk.LabelFrame(tab, text="Available Algorithms", padding=10)
        algo_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        algorithms = [
            ("Minimum Spanning Tree (Prim)", "mst"),
            ("Shortest Path (Dijkstra)", "dijkstra"),
            ("All-Pairs Shortest Path (Floyd)", "floyd"),
            ("Network Flow Analysis", "flow"),
            ("Clustering Coefficient", "clustering"),
        ]
        
        for algo_text, algo_id in algorithms:
            ttk.Radiobutton(algo_frame, text=algo_text, variable=self.selected_algorithm, 
                          value=algo_id).pack(anchor=tk.W, pady=5)
        
        self._add_button(algo_frame, "Execute Algorithm", self._on_execute_algorithm)

    def _show_frame(self, frame_name: str):
        """Switch to specified frame."""
        if frame_name in self.frames:
            frame = self.frames[frame_name]
            frame.tkraise()
            frame.grid(row=0, column=0, sticky="nsew")
            self.current_frame = frame_name

    def _check_queue(self):
        """Check for results from worker threads."""
        try:
            while True:
                msg = self.result_queue.get_nowait()
                if msg['type'] == 'result_page':
                    self._create_and_show_result_page(msg['title'], msg['data'])
                elif msg['type'] == 'info':
                    messagebox.showinfo(msg['title'], msg['data'])
                elif msg['type'] == 'error':
                    messagebox.showerror("Error", msg['data'])
                elif msg['type'] == 'graph_update':
                    self._draw_graph(msg.get('highlight'), msg.get('colors'))
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)

    def _create_and_show_result_page(self, title, data):
        """Create result page dynamically and show it."""
        # Clean up old result frame if exists
        if 'result' in self.frames:
            self.frames['result'].destroy()
            
        result_frame = ResultPage(
            self.container, 
            title, 
            data,
            lambda: self._show_frame('dashboard')
        )
        result_frame.grid(row=0, column=0, sticky="nsew")
        self.frames['result'] = result_frame
        self._show_frame('result')

    def _run_task(self, func: Callable, title: str) -> None:
        """Run a function with loading dialog and result handling."""
        loading = LoadingDialog(self, f"{title}...")
        
        def worker():
            try:
                result = func()
                if result: # If function returns string, show it on result page
                    self.result_queue.put({'type': 'result_page', 'title': title, 'data': result})
            except Exception as e:
                logger.error(f"Task error: {e}")
                self.result_queue.put({'type': 'error', 'data': str(e)})
            finally:
                # Close loading dialog via main thread
                self.after(0, loading.destroy)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    @staticmethod
    def _add_button(parent: ttk.Frame, text: str, command) -> ttk.Button:
        btn = ttk.Button(parent, text=text, command=command)
        btn.pack(fill=tk.X, pady=5)
        return btn

    def _draw_graph(self, highlight_edges=None, node_colors=None):
        """Draw the network graph on the canvas."""
        try:
            self.ax.clear()
            pos = nx.spring_layout(self.G, seed=ApplicationConfig.FIGURE_SEED)
            
            # Draw base graph
            nx.draw(
                self.G, pos, ax=self.ax, with_labels=True,
                node_color=node_colors if node_colors else ApplicationConfig.NODE_DEFAULT_COLOR,
                node_size=ApplicationConfig.NODE_SIZE,
                edge_color=ApplicationConfig.EDGE_DEFAULT_COLOR
            )
            
            # Draw weights
            edge_labels = nx.get_edge_attributes(self.G, "weight")
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, ax=self.ax)
            
            # Highlights
            if highlight_edges:
                nx.draw_networkx_edges(
                    self.G, pos, edgelist=highlight_edges,
                    edge_color=ApplicationConfig.HIGHLIGHT_COLOR,
                    width=ApplicationConfig.HIGHLIGHT_WIDTH,
                    ax=self.ax
                )
            
            self.canvas.draw()
        except Exception as e:
            logger.error(f"Draw error: {e}")

    # ===== Logic & Analytics =====
    
    def _on_refresh_analytics(self) -> None:
        self._calculate_metrics()
        self._display_analytics()
    
    def _display_analytics(self) -> None:
        if not self.metrics: return
        
        text = f"""
NETWORK ANALYTICS DASHBOARD
---------------------------
Density: {self.metrics.density:.4f}
Avg Clustering: {self.metrics.avg_clustering:.4f}
Avg Path Length: {self.metrics.avg_path_length:.2f}
Diameter: {self.metrics.diameter}
Avg Degree: {self.metrics.avg_degree:.2f}

Connected: {'Yes' if nx.is_connected(self.G) else 'No'}
Nodes: {self.G.number_of_nodes()}
Edges: {self.G.number_of_edges()}
"""
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, text)
        self.metrics_text.config(state=tk.DISABLED)

    def _on_reset_network(self):
        self.G = self.G_original.copy()
        self._calculate_metrics()
        self._display_analytics()
        self._draw_graph()
        messagebox.showinfo("Success", "Network reset to default topology.")

    def _on_generate_mst(self):
        def task():
            mst = nx.minimum_spanning_tree(self.G, algorithm="prim")
            total_weight = sum(d['weight'] for u,v,d in mst.edges(data=True))
            
            # Update UI from main thread
            self.result_queue.put({'type': 'graph_update', 'highlight': list(mst.edges())})
            
            return f"MST Generated via Prim's Algorithm.\nTotal Weight: {total_weight}\nEdges: {list(mst.edges())}"
        
        self._run_task(task, "Calculating MST")

    def _on_show_paths(self):
        def task():
            if not nx.has_path(self.G, 1, 8):
                return "No path between Node 1 and Node 8"
                
            paths = list(nx.edge_disjoint_paths(self.G, 1, 8))
            
            # Flatten paths for visual highlight
            highlight = []
            for path in paths:
                highlight.extend(zip(path, path[1:]))
            
            self.result_queue.put({'type': 'graph_update', 'highlight': highlight})
            
            report = f"Edge-Disjoint Paths (Node 1 -> Node 8):\nCount: {len(paths)}\n\n"
            for i, p in enumerate(paths, 1):
                report += f"Path {i}: {p}\n"
            return report
            
        self._run_task(task, "Finding Disjoint Paths")

    def _on_simulate_failure(self):
        if not self.G.nodes(): return
        node = random.choice(list(self.G.nodes()))
        self.G.remove_node(node)
        self._draw_graph()
        self._on_refresh_analytics()
        messagebox.showwarning("Simulation", f"Node {node} has failed and was removed.")

    def _on_optimize_tree(self):
        # Simplified for visualization: build a generic balanced structure from current nodes
        nodes = sorted(list(self.G.nodes()))
        height = int(np.ceil(np.log2(len(nodes) + 1)))
        messagebox.showinfo("Optimization", f"Balanced Command Tree Height required: {height}\nNodes: {nodes}")

    def _on_graph_coloring(self):
        def task():
            colors_map = nx.coloring.greedy_color(self.G, strategy="largest_first")
            node_colors = [ApplicationConfig.COLOR_MAP.get(colors_map[n], "gray") for n in self.G.nodes()]
            self.result_queue.put({'type': 'graph_update', 'colors': node_colors})
            return f"Graph Coloring Complete.\nChromatic Number: {max(colors_map.values())+1}\nMapping: {colors_map}"
        
        self._run_task(task, "Graph Coloring")

    def _on_centrality_analysis(self):
        def task():
            bc = nx.betweenness_centrality(self.G)
            sorted_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)
            return "Betweenness Centrality (Top Nodes):\n" + "\n".join([f"Node {n}: {v:.4f}" for n,v in sorted_bc])
        
        self._run_task(task, "Centrality Analysis")

    def _on_execute_algorithm(self):
        algo = self.selected_algorithm.get()
        if algo == "mst":
            self._on_generate_mst()
        elif algo == "dijkstra":
            self._on_dijkstra()
        elif algo == "floyd":
            self._on_floyd()
        elif algo == "flow":
            self._on_flow()
        elif algo == "clustering":
            self._on_clustering()

    def _on_dijkstra(self):
        def task():
            if not nx.has_path(self.G, 1, 8): return "No path."
            path = nx.dijkstra_path(self.G, 1, 8, weight='weight')
            length = nx.dijkstra_path_length(self.G, 1, 8, weight='weight')
            
            highlight = list(zip(path, path[1:]))
            self.result_queue.put({'type': 'graph_update', 'highlight': highlight})
            
            return f"Shortest Path (Dijkstra) Node 1 -> 8:\nPath: {path}\nTotal Weight: {length}"
        self._run_task(task, "Dijkstra Algorithm")

    def _on_floyd(self):
        def task():
            # Floyd-Warshall is O(V^3), fine for small N
            path_lengths = dict(nx.all_pairs_dijkstra_path_length(self.G, weight='weight'))
            return f"All-Pairs Shortest Path Calculated.\nData for {len(path_lengths)} nodes ready."
        self._run_task(task, "Floyd-Warshall")

    def _on_flow(self):
        def task():
            val, _ = nx.maximum_flow(self.G, 1, 8, capacity='capacity')
            return f"Maximum Network Flow (1 -> 8): {val}"
        self._run_task(task, "Max Flow Analysis")
    
    def _on_clustering(self):
        def task():
            cc = nx.average_clustering(self.G)
            return f"Average Clustering Coefficient: {cc:.4f}"
        self._run_task(task, "Clustering Analysis")


if __name__ == "__main__":
    try:
        app = EmergencyNetworkSimulator()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Application crash: {e}")