import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import subprocess
	
class DiskSchedulingVisualizer:
    # Disk parameters constants
    RPM = 7200            # Disk rotation speed
    SECTOR_SIZE = 512     # Bytes per sector
    TRACKS_PER_CYLINDER = 1  # For simplicity
    SEEK_RATE = 0.1       # ms per cylinder seek
    TRANSFER_RATE = 1     # MB/s

    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Algorithm Visualizer")
        self.root.geometry("1200x800")
        
        # Dark mode toggle
        self.dark_mode = False
        self.bg_color = "white"
        self.fg_color = "black"
        
        # Variables
        self.requests = []
        self.head_pos = 50
        self.disk_size = 200
        self.direction = 1  # 1 for right, 0 for left
        self.selected_algorithm = "FCFS"
        
        # Create UI
        self.create_widgets()
        self.toggle_theme()

    def create_widgets(self):
        # Control Frame
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Algorithm Selection
        algo_frame = tk.LabelFrame(control_frame, text="Algorithm Parameters", padx=5, pady=5)
        algo_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(algo_frame, text="Select Algorithm:").pack(anchor=tk.W)
        self.algo_combo = ttk.Combobox(algo_frame, values=[
            "FCFS", "SSTF", "SCAN", "LOOK", "C-SCAN", "C-LOOK"
        ])
        self.algo_combo.pack(fill=tk.X, pady=5)
        self.algo_combo.set("FCFS")
        self.create_tooltip(self.algo_combo, "First-Come First-Served (FCFS)\n"
                           "Shortest Seek Time First (SSTF)\n"
                           "SCAN (Elevator)\nLOOK\nC-SCAN\nC-LOOK")
        
        # Disk Parameters
        disk_frame = tk.LabelFrame(control_frame, text="Disk Parameters", padx=5, pady=5)
        disk_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(disk_frame, text="Disk Size (cylinders):").pack(anchor=tk.W)
        self.disk_size_slider = tk.Scale(disk_frame, from_=100, to=500, orient=tk.HORIZONTAL)
        self.disk_size_slider.set(200)
        self.disk_size_slider.pack(fill=tk.X, pady=5)
        
        tk.Label(disk_frame, text="Initial Head Position:").pack(anchor=tk.W)
        self.head_pos_slider = tk.Scale(disk_frame, from_=0, to=self.disk_size_slider.get()-1, orient=tk.HORIZONTAL)
        self.head_pos_slider.set(50)
        self.head_pos_slider.pack(fill=tk.X, pady=5)
        
        # Update head position slider when disk size changes
        def update_head_pos_max(*args):
            self.head_pos_slider.config(to=self.disk_size_slider.get()-1)
        self.disk_size_slider.config(command=update_head_pos_max)
        
        # Direction Selection
        dir_frame = tk.LabelFrame(control_frame, text="Initial Direction", padx=5, pady=5)
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.direction_var = tk.IntVar(value=1)
        tk.Radiobutton(dir_frame, text="Right (Increasing)", variable=self.direction_var, value=1).pack(anchor=tk.W)
        tk.Radiobutton(dir_frame, text="Left (Decreasing)", variable=self.direction_var, value=0).pack(anchor=tk.W)
        
        # Request Input
        req_frame = tk.LabelFrame(control_frame, text="Disk Requests", padx=5, pady=5)
        req_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(req_frame, text="Cylinder Numbers (comma separated):").pack(anchor=tk.W)
        self.request_entry = tk.Entry(req_frame,fg='white',bg='black',insertbackground='black',relief='solid',borderwidth=1  )
        self.request_entry.pack(fill=tk.X, pady=5)
        self.request_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")
        
        # Buttons
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="Random", command=self.generate_random, bg="#4a9cff", fg="white", width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Visualize", command=self.visualize, bg="green", fg="white", width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Compare All", command=self.compare_all, bg="blue", fg="white", width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Clear", command=self.clear, bg="red", fg="white", width=10).pack(side=tk.LEFT, padx=2)
        
        # Bottom buttons
        bottom_frame = tk.Frame(control_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(bottom_frame, text="Dark Mode", command=self.toggle_theme).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Visualization Frame
        vis_frame = tk.Frame(self.root)
        vis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Matplotlib Figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]})
        self.canvas = FigureCanvasTkAgg(self.fig, master=vis_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Results Frame
        self.result_text = tk.Text(vis_frame, height=10, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(vis_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        self.result_text.pack(fill=tk.X)
        self.result_text.insert(tk.END, "Welcome to Disk Scheduling Visualizer!\n"
                              "Enter requests and click Visualize to begin.")

    def create_tooltip(self, widget, text):
        tooltip = ttk.Label(self.root, text=text, background="#ffffe0", 
                          relief="solid", borderwidth=1, padding=5)
        def enter(event):
            tooltip.place(x=widget.winfo_rootx(), y=widget.winfo_rooty()-30)
        def leave(event):
            tooltip.place_forget()
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.fg_color = "#2d2d2d" if self.dark_mode else "white"
        self.bg_color = "white" if self.dark_mode else "black"
        self.highlight_color = "#4a9cff" if self.dark_mode else "#1a73e8"
        
        # Update root and all widgets
        self.root.config(bg=self.bg_color)
        for widget in self.root.winfo_children():
            self.update_widget_theme(widget)
        
        # Update matplotlib theme
        self.fig.set_facecolor(self.bg_color)
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor(self.bg_color)
            ax.title.set_color(self.fg_color)
            ax.xaxis.label.set_color(self.fg_color)
            ax.yaxis.label.set_color(self.fg_color)
            ax.tick_params(colors=self.fg_color)
            for spine in ax.spines.values():
                spine.set_color(self.fg_color)
        self.canvas.draw()

    def update_widget_theme(self, widget):
        try:
            if isinstance(widget, (tk.Frame, ttk.Frame)):
                widget.config(bg=self.bg_color)
            elif isinstance(widget, (tk.Label, tk.Button, tk.Radiobutton, tk.Text)):
                widget.config(bg=self.bg_color, fg=self.fg_color)
            elif isinstance(widget, tk.Entry):
                widget.config(bg="white" if not self.dark_mode else "#333333", 
                            fg="black" if not self.dark_mode else "white",
                            insertbackground=self.fg_color)
            elif isinstance(widget, ttk.Combobox):
                style = ttk.Style()
                style.theme_use('clam')
                style.configure('TCombobox', 
                              fieldbackground="white" if not self.dark_mode else "#333333",
                              background="white" if not self.dark_mode else "#333333",
                              foreground="black" if not self.dark_mode else "white")
            
            # Update children recursively
            for child in widget.winfo_children():
                self.update_widget_theme(child)
        except:
            pass

    def generate_random(self):
        num_requests = random.randint(5, 15)
        max_cyl = self.disk_size_slider.get()
        requests = sorted(random.sample(range(0, max_cyl), num_requests))
        self.request_entry.delete(0, tk.END)
        self.request_entry.insert(0, ", ".join(map(str, requests)))

    def parse_requests(self):
        try:
            req_text = self.request_entry.get().strip()
            if not req_text:
                raise ValueError("No requests entered")
                
            self.requests = [int(x.strip()) for x in req_text.split(",") if x.strip()]
            if not self.requests:
                raise ValueError("No valid requests found")
                
            # Validate disk size and head position
            self.disk_size = self.disk_size_slider.get()
            self.head_pos = self.head_pos_slider.get()
            if self.head_pos >= self.disk_size:
                raise ValueError("Head position must be less than disk size")
                
            # Validate all requests are within disk bounds
            for req in self.requests:
                if req >= self.disk_size or req < 0:
                    raise ValueError(f"Request {req} exceeds disk bounds (0-{self.disk_size-1})")
                    
            self.direction = self.direction_var.get()
            self.selected_algorithm = self.algo_combo.get()
            return True
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return False

    def run_algorithm(self, algorithm):
        if not self.parse_requests():
            return None, None, None, None, None, None  # total_movement, seek, rot, xfer, total, sequence
    
        try:
            cmd = [r"C:\Users\JAREENA\Desktop\Loan_Data\sem4 report\OS\DiskScheduling.exe",algorithm, str(self.head_pos),
                   str(self.disk_size), str(self.direction)] + [str(r) for r in self.requests]
            
            # Run with no console window
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            output = result.stdout.strip()
            
            print(f"Debug - {algorithm} Output:", output)  # For troubleshooting
            
            if not output or "|" not in output:
                raise ValueError("C program returned empty or invalid output")
            
            parts = output.split("|")
            if len(parts) < 6:
                raise ValueError(f"Expected 6 data parts, got {len(parts)}")
            
            # Convert and validate all values
            total_movement = int(parts[0])
            seek_time = float(parts[1])
            rotational_latency = float(parts[2])
            transfer_time = float(parts[3])
            total_time = float(parts[4])
            sequence = [int(x) for x in parts[5].split(",") if x.strip()]
            
            # Validate sequence matches movement
            if len(sequence) < 2:
                raise ValueError("Invalid movement sequence from C program")
                
            return total_movement, seek_time, rotational_latency, transfer_time, total_time, sequence
            
        except Exception as e:
            error_msg = f"Algorithm {algorithm} failed:\n{str(e)}"
            if 'output' in locals():
                error_msg += f"\nRaw output: {output}"
            messagebox.showerror("Execution Error", error_msg)
            return None, None, None, None, None, None

    def visualize(self):
        result = self.run_algorithm(self.selected_algorithm)
        if None in result[:5]:  # Check first five values
            return
            
        total_movement, seek_time, rot_latency, transfer_time, total_time, sequence = result
        
        # Clear and setup plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Plot 1: Movement Visualization
        self.ax1.set_title(f"{self.selected_algorithm} - Seek Pattern (Total Movement: {total_movement} cylinders)",pad=-7)
        self.ax1.set_xlabel("Cylinder Number",labelpad=-4)
        self.ax1.set_ylabel("Movement Step")
        self.ax1.set_xlim(-5, self.disk_size+5)
        self.ax1.set_ylim(-1, len(sequence)+1)
        
        # Draw movement path with arrows
        for i in range(len(sequence)-1):
            self.ax1.annotate('', xy=(sequence[i+1], i+1), xytext=(sequence[i], i),
                            arrowprops=dict(arrowstyle='->', color='red', lw=1.5, alpha=0.7))
        
        # Mark key points
        self.ax1.scatter([sequence[0]], [0], color='green', s=100, label='Start Head', zorder=5)
        self.ax1.scatter(self.requests, [0]*len(self.requests), color='blue', 
                        label='Requests', alpha=0.7, zorder=4)
        
        # Add direction indicator if applicable
        if self.selected_algorithm in ["SCAN", "LOOK", "C-SCAN", "C-LOOK"]:
            dir_text = "Right" if self.direction else "Left"
            self.ax1.text(0.02, 0.95, f"Direction: {dir_text}", 
                         transform=self.ax1.transAxes, color='purple',
                         bbox=dict(facecolor=self.bg_color, alpha=0.8))
        
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)
        
        # Plot 2: Timeline
        served_order = sequence[1:]
        self.ax2.set_title("Request Service Timeline",pad=0)
        self.ax2.set_xlabel("Service Order")
        self.ax2.set_ylabel("Cylinder Number")
        self.ax2.step(range(len(served_order)), served_order, where='post', 
                     color='purple', label=f'Total Time: {total_time:.2f}ms')
        self.ax2.scatter(range(len(served_order)), served_order, color='red', alpha=0.7)
        
        # Annotate points
        for i, (x, y) in enumerate(zip(range(len(served_order)), served_order)):
            self.ax2.annotate(f'{y}', (x, y), textcoords="offset points",
                             xytext=(0,8), ha='center', fontsize=8)
        
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
        
        # Update results display
        self.update_results_text(total_movement, seek_time, rot_latency, 
                               transfer_time, total_time, sequence)
        
        self.canvas.draw()

    def update_results_text(self, movement, seek, rot, xfer, total, sequence):
        self.result_text.delete(1.0, tk.END)
        
        # Format the metrics display
        metrics = [
            "DISK ACCESS PERFORMANCE METRICS",
            "═" * 50,
            f"{'Seek Time (head movement)':<30}: {seek:.2f} ms",
            f"{'Rotational Latency':<30}: {rot:.2f} ms",
            f"{'Data Transfer Time':<30}: {xfer:.2f} ms",
            "─" * 30 + " TOTAL " + "─" * 13,
            f"{'TOTAL ACCESS TIME':<30}: {total:.2f} ms",
            f"{'Total Head Movement':<30}: {movement} cylinders",
            "═" * 50,
            "SERVICE ORDER:",
            " → ".join(map(str, sequence))
        ]
        
        # Insert with formatting
        self.result_text.insert(tk.END, "\n".join(metrics))
        
        # Configure tags for styling
        self.result_text.tag_configure("header", font=('TkDefaultFont', 10, 'bold'))
        self.result_text.tag_add("header", "1.0", "1.end")
        self.result_text.tag_add("header", "8.0", "8.end")
        
        self.result_text.tag_configure("highlight", foreground="blue")
        self.result_text.tag_add("highlight", "6.0", "6.end")

    def compare_all(self):
        if not self.parse_requests():
            return
        
        algorithms = ["FCFS", "SSTF", "SCAN", "LOOK", "C-SCAN", "C-LOOK"]
        results = []
        
        # Run all algorithms
        for algo in algorithms:
            result = self.run_algorithm(algo)
            if None not in result[:5]:  # Only use valid results
                results.append({
                    "algorithm": algo,
                    "total_movement": result[0],
                    "seek_time": result[1],
                    "rot_latency": result[2],
                    "transfer_time": result[3],
                    "total_time": result[4],
                    "sequence": result[5]
                })
        
        if not results:
            messagebox.showwarning("Comparison", "No valid results to compare")
            return
        
        # Display detailed comparison
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "ALGORITHM COMPARISON RESULTS\n")
        self.result_text.insert(tk.END, "═" * 50 + "\n")
        self.result_text.insert(tk.END, 
            f"{'Algorithm':<10}{'Seek':<8}{'Rot':<8}{'Xfer':<8}{'Total':<10}{'Movement'}\n")
        self.result_text.insert(tk.END, "─" * 50 + "\n")
        
        for res in results:
            self.result_text.insert(tk.END, 
                f"{res['algorithm']:<10}{res['seek_time']:.2f} {res['rot_latency']:.2f} "
                f"{res['transfer_time']:.2f} {res['total_time']:.2f} {res['total_movement']}\n")
        
        # Highlight best algorithm
        best = min(results, key=lambda x: x['total_time'])
        self.result_text.insert(tk.END, "═" * 50 + "\n")
        self.result_text.insert(tk.END, 
            f"BEST: {best['algorithm']} ({best['total_time']:.2f} ms, {best['total_movement']} cylinders)\n")
        
        # Configure text tags
        self.result_text.tag_configure("best", foreground="green", font=('TkDefaultFont', 10, 'bold'))
        self.result_text.tag_add("best", f"{len(results)+5}.0", f"{len(results)+5}.end")
        
        # Plot comparison
        self.ax1.clear()
        self.ax2.clear()
        
        # Prepare data
        x = [res['algorithm'] for res in results]
        y_seek = [res['seek_time'] for res in results]
        y_rot = [res['rot_latency'] for res in results]
        y_xfer = [res['transfer_time'] for res in results]
        
        # Create stacked bar chart
        p1 = self.ax1.bar(x, y_seek, label='Seek Time', color='#1f77b4')
        self.ax1.tick_params(axis='x', pad=11)  # 10 points of space between ticks and labels
        p2 = self.ax1.bar(x, y_rot, bottom=y_seek, label='Rotational Latency', color='green')
        p3 = self.ax1.bar(x, y_xfer, bottom=[i+j for i,j in zip(y_seek,y_rot)], 
                         label='Transfer Time', color='black')
        
        self.ax1.set_title("Time Components by Algorithm")
        self.ax1.set_ylabel("Time (ms)")
        self.ax1.legend()
        
        # Add value labels
        for i, res in enumerate(results):
            self.ax1.text(i, res['total_time']+1, f"{res['total_time']:.1f}ms", ha='center', fontsize=8)
            self.ax1.text(i, -3, f"{res['total_movement']} cyl", ha='center', fontsize=8)
        
        # Second plot for movement comparison
        self.ax2.bar(x, [res['total_movement'] for res in results], color='#9467bd')
        self.ax2.set_title("Total Head Movement Comparison",pad=0)
        self.ax2.set_ylabel("Cylinders")
        
        self.canvas.draw()

    def clear(self):
        self.request_entry.delete(0, tk.END)
        self.request_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")
        self.head_pos_slider.set(50)
        self.disk_size_slider.set(200)
        self.direction_var.set(1)
        self.algo_combo.set("FCFS")
        self.ax1.clear()
        self.ax2.clear()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Ready for new simulation...")
        self.canvas.draw()
if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulingVisualizer(root)
    root.mainloop()

