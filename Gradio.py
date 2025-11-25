# app_gradio.py - ELECTRICITY OPERATIONS INTELLIGENCE (EOI-1912)
import gradio as gr
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------------
# Sample Data Generation
# -------------------------
def generate_sample_complaints():
    """Generate sample complaint data"""
    np.random.seed(42)
    sample_data = {
        'Request_Id': [f'REQ{str(i).zfill(3)}' for i in range(1, 21)],
        'Feeder_MSN': [f'FDR{str(i).zfill(3)}' for i in range(1, 21)],
        'Feeder_ProcessStatus': np.random.choice(['success', 'fail'], 20, p=[0.7, 0.3]),
        'DTR_MSN': [f'DTR{str(i).zfill(3)}' for i in range(1, 21)],
        'DTR_ProcessStatus': np.random.choice(['success', 'fail'], 20, p=[0.6, 0.4]),
        'Consumer_MSN': [f'CON{str(i).zfill(3)}' for i in range(1, 21)],
        'Consumer_ProcessStatus': np.random.choice(['success', 'fail'], 20, p=[0.5, 0.5]),
        'Consumer_Phase_Id': np.random.choice([1, 3], 20, p=[0.3, 0.7]),
        'f_vr': np.round(np.random.uniform(220, 240, 20), 1),
        'f_vy': np.round(np.random.uniform(220, 240, 20), 1),
        'f_vb': np.round(np.random.uniform(220, 240, 20), 1),
        'f_ir': np.round(np.random.uniform(0.5, 2.0, 20), 2),
        'f_iy': np.round(np.random.uniform(0.5, 2.0, 20), 2),
        'f_ib': np.round(np.random.uniform(0.5, 2.0, 20), 2),
        'd_vr': np.round(np.random.uniform(220, 240, 20), 1),
        'd_vy': np.round(np.random.uniform(220, 240, 20), 1),
        'd_vb': np.round(np.random.uniform(220, 240, 20), 1),
        'd_ir': np.round(np.random.uniform(0.1, 1.5, 20), 2),
        'd_iy': np.round(np.random.uniform(0.1, 1.5, 20), 2),
        'd_ib': np.round(np.random.uniform(0.1, 1.5, 20), 2),
        'Final_Label': np.random.choice(['DTHT', 'DTLT', 'FOC', 'FOC/DT HT'], 20),
        'region': np.random.choice(['Region A', 'Region B', 'Region C'], 20),
        'circle': np.random.choice(['Circle 1', 'Circle 2', 'Circle 3'], 20),
        'division': np.random.choice(['Division X', 'Division Y', 'Division Z'], 20),
        'zone': np.random.choice(['Zone P', 'Zone Q', 'Zone R'], 20)
    }
    return pd.DataFrame(sample_data)

# -------------------------
# Application Functions
# -------------------------
def fetch_complaints():
    """Step 1: Fetch live complaints"""
    complaints_df = generate_sample_complaints()
    num_complaints = min(random.randint(5, 8), len(complaints_df))
    selected_complaints = complaints_df.sample(n=num_complaints)
    
    # Format complaints for display
    complaint_list = []
    for idx, complaint in selected_complaints.iterrows():
        current_time = datetime.now()
        complaint_time = current_time - timedelta(minutes=random.randint(2, 3))
        
        complaint_info = f"""
        🚨 **Request ID:** {complaint['Request_Id']}
        ⏰ **Complaint Time:** {complaint_time.strftime('%H:%M:%S')}
        📍 **Location:** {complaint['region']} → {complaint['circle']} → {complaint['division']} → {complaint['zone']}
        🔄 **Status:** ⏳ PENDING ANALYSIS
        {'-' * 50}
        """
        complaint_list.append(complaint_info)
    
    return "\n".join(complaint_list), selected_complaints

def analyze_complaints(selected_complaints):
    """Step 2: Analyze complaints"""
    if selected_complaints.empty:
        return "No complaints to analyze", None, None
    
    analysis_results = []
    
    for i, (idx, complaint) in enumerate(selected_complaints.iterrows()):
        analysis = f"""
        📋 **Complaint #{i+1} - {complaint['Request_Id']}**
        
        🔍 **Ping Status:**
        • Feeder: {'✅ SUCCESS' if complaint['Feeder_ProcessStatus'] == 'success' else '❌ FAIL'}
        • DTR: {'✅ SUCCESS' if complaint['DTR_ProcessStatus'] == 'success' else '❌ FAIL'} 
        • Consumer: {'✅ SUCCESS' if complaint['Consumer_ProcessStatus'] == 'success' else '❌ FAIL'}
        
        📈 **Intensity Profile:**
        **Feeder:** V(R/Y/B): {complaint['f_vr']:.1f}/{complaint['f_vy']:.1f}/{complaint['f_vb']:.1f}V
                 I(R/Y/B): {complaint['f_ir']:.2f}/{complaint['f_iy']:.2f}/{complaint['f_ib']:.2f}A
        **DTR:** V(R/Y/B): {complaint['d_vr']:.1f}/{complaint['d_vy']:.1f}/{complaint['d_vb']:.1f}V
               I(R/Y/B): {complaint['d_ir']:.2f}/{complaint['d_iy']:.2f}/{complaint['d_ib']:.2f}A
        
        🎯 **Predicted Fault:** {complaint['Final_Label']}
        {'='*60}
        """
        analysis_results.append(analysis)
    
    # Create visualizations
    fault_counts = selected_complaints['Final_Label'].value_counts()
    
    # Pie chart
    fig_pie = px.pie(
        values=fault_counts.values,
        names=fault_counts.index,
        title="Fault Type Distribution",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    
    # Bar chart
    fig_bar = px.bar(
        x=fault_counts.index,
        y=fault_counts.values,
        title="Fault Count by Type",
        labels={'x': 'Fault Type', 'y': 'Count'},
        color=fault_counts.values,
        color_continuous_scale='blues'
    )
    
    return "\n".join(analysis_results), fig_pie, fig_bar

def predict_etr(selected_complaints):
    """Step 3: Predict ETR"""
    if selected_complaints.empty:
        return "No complaints for ETR prediction", None
    
    etr_results = []
    
    for idx, complaint in selected_complaints.iterrows():
        base_etr = random.randint(30, 180)
        etr_minutes = base_etr
        etr_human = f"{etr_minutes//60} hr {etr_minutes%60} min" if etr_minutes >= 60 else f"{etr_minutes} min"
        
        etr_info = f"""
        🔧 **Request ID:** {complaint['Request_Id']}
        ⚡ **Fault Type:** {complaint['Final_Label']}
        ⏱️ **Estimated Restoration Time:** {etr_human}
        📍 **Location:** {complaint['region']} → {complaint['circle']} → {complaint['division']} → {complaint['zone']}
        {'-'*50}
        """
        etr_results.append(etr_info)
    
    return "\n".join(etr_results), selected_complaints

# -------------------------
# Gradio Interface
# -------------------------
def create_interface():
    # State to store complaints between steps
    complaints_state = gr.State(pd.DataFrame())
    
    with gr.Blocks(theme=gr.themes.Soft(), title="ELECTRICITY OPERATIONS INTELLIGENCE (EOI-1912)") as demo:
        gr.Markdown(
            """
            # ⚡ ELECTRICITY OPERATIONS INTELLIGENCE (EOI-1912)
            ### Advanced Fault Detection • Predictive Analytics • Automated Restoration
            *Real-time Monitoring | AI-Powered Diagnostics | Smart Grid Management*
            """
        )
        
        with gr.Tabs():
            # Tab 1: Main Workflow
            with gr.TabItem("🚀 Main Workflow"):
                gr.Markdown("## 📋 Complete Fault Analysis Workflow")
                
                with gr.Row():
                    with gr.Column():
                        fetch_btn = gr.Button("📥 Step 1: Fetch Live Complaints", variant="primary", size="lg")
                    
                    with gr.Column():
                        analyze_btn = gr.Button("🔍 Step 2: Analyze Complaints", variant="secondary", size="lg")
                    
                    with gr.Column():
                        etr_btn = gr.Button("⏱️ Step 3: Predict ETR", variant="secondary", size="lg")
                
                with gr.Row():
                    with gr.Column():
                        complaints_output = gr.Textbox(
                            label="📋 Live Complaints",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                    
                    with gr.Column():
                        analysis_output = gr.Textbox(
                            label="🔍 Analysis Results", 
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                with gr.Row():
                    with gr.Column():
                        pie_chart = gr.Plot(label="📊 Fault Distribution")
                    
                    with gr.Column():
                        bar_chart = gr.Plot(label="📈 Fault Counts")
                
                with gr.Row():
                    etr_output = gr.Textbox(
                        label="⏱️ ETR Predictions",
                        lines=10,
                        max_lines=15,
                        show_copy_button=True
                    )
            
            # Tab 2: Fault Information
            with gr.TabItem("🔍 Fault Information"):
                gr.Markdown("## ⚡ Fault Types & Information")
                
                fault_info = {
                    "DTHT": {
                        "meaning": "DT ke 3 phase voltages me >30% imbalance",
                        "analogy": "Transformer me kuch gadbad / phase loss",
                        "description": "Distribution Transformer High Imbalance - Significant voltage imbalance across three phases"
                    },
                    "DTLT": {
                        "meaning": "Voltage OK but 1 phase current ZERO",
                        "analogy": "Wire cut / LT line broken", 
                        "description": "Distribution Transformer Low Current - One phase has zero current indicating broken line"
                    },
                    "FOC": {
                        "meaning": "DT OK, supply consumer tak aa rahi hai, ping nahi",
                        "analogy": "Ghar ka MCB trip / internal wiring issue",
                        "description": "Failure at Consumer End - Power reaching consumer premises but internal issue detected"
                    },
                    "FOC/DT HT": {
                        "meaning": "DT readings NULL, ping patterns decide fault",
                        "analogy": "DT meter dead / communication fail",
                        "description": "DT Communication Failure - Transformer meter offline, using ping patterns for diagnosis"
                    }
                }
                
                for fault, info in fault_info.items():
                    with gr.Accordion(f"⚡ {fault}", open=False):
                        gr.Markdown(f"""
                        **Meaning:** {info['meaning']}
                        
                        **Analogy:** {info['analogy']}
                        
                        **Description:** {info['description']}
                        """)
            
            # Tab 3: System Status
            with gr.TabItem("📊 System Status"):
                gr.Markdown("## 🖥️ System Status & Quick Actions")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🔧 Model Status")
                        gr.Markdown("""
                        - Fault Model: ✅ Available
                        - ETR Model: ✅ Available  
                        - Data Pipeline: ✅ Active
                        """)
                    
                    with gr.Column():
                        gr.Markdown("### 📈 Data Status")
                        gr.Markdown("""
                        - Live Complaints: 20+
                        - Regions: 3 Active
                        - Analysis Queue: Ready
                        """)
                
                with gr.Row():
                    reset_btn = gr.Button("🔄 Reset Workflow", variant="secondary")
                    report_btn = gr.Button("📊 Generate Report", variant="secondary")
                
                reset_output = gr.Textbox(label="System Messages", interactive=False)
        
        # Event handlers
        fetch_btn.click(
            fn=fetch_complaints,
            outputs=[complaints_output, complaints_state]
        )
        
        analyze_btn.click(
            fn=analyze_complaints,
            inputs=[complaints_state],
            outputs=[analysis_output, pie_chart, bar_chart]
        )
        
        etr_btn.click(
            fn=predict_etr,
            inputs=[complaints_state],
            outputs=[etr_output, complaints_state]
        )
        
        def reset_workflow():
            return "🔄 Workflow reset successfully! You can start from Step 1."
        
        reset_btn.click(
            fn=reset_workflow,
            outputs=reset_output
        )
        
        report_btn.click(
            fn=lambda: "📊 Report generation feature coming soon!",
            outputs=reset_output
        )
        
        gr.Markdown("---")
        gr.Markdown("<center>Built for 1912 Automation • Esyasoft Technologies</center>")
    
    return demo

# -------------------------
# Launch Application
# -------------------------
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Creates public URL
        show_error=True
    )