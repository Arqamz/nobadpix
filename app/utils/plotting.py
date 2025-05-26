import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def generate_severity_plot_base64(categories_data: dict) -> str | None:
    """
    Generates a Matplotlib/Seaborn bar plot for severity scores and returns it as a Base64 encoded PNG string.
    categories_data: A dictionary like {'hate': 0, 'sexual': 2, ...}
    """
    if not categories_data:
        return None

    # Map Azure severity values (0, 2, 4, 6) to a more linear scale for plotting if desired,
    # or use them directly. For simplicity, we use them directly here.
    # We also define labels for these severities for better plot understanding.
    severity_map = {
        0: "Very Low",
        2: "Low",
        4: "Medium",
        6: "High"
    }
    # Ensure all expected categories are present, defaulting to 0 if not returned by Azure
    default_categories = ["hate", "self_harm", "sexual", "violence"]
    plot_data = {cat: categories_data.get(cat, 0) for cat in default_categories}
    
    categories = [cat.replace("_", " ").title() for cat in plot_data.keys()]
    severities = list(plot_data.values())

    # Use a Seaborn style for nicer aesthetics
    sns.set_theme(style="whitegrid")
    
    fig, ax = plt.subplots(figsize=(7, 4)) # Adjusted figure size for better fit
    
    # Create a color palette based on severity (example)
    # You can customize these colors extensively
    palette = []
    for sev in severities:
        if sev == 6:
            palette.append('#d9534f') # Red (High)
        elif sev == 4:
            palette.append('#f0ad4e') # Orange (Medium)
        elif sev == 2:
            palette.append('#5cb85c') # Green (Low)
        else:
            palette.append('#5bc0de') # Blue (Very Low)

    bars = sns.barplot(x=categories, y=severities, ax=ax, palette=palette, hue=categories, dodge=False, legend=False)

    ax.set_title('Content Moderation Severity Levels', fontsize=14)
    ax.set_ylabel('Severity Score', fontsize=10)
    ax.set_xlabel('Category', fontsize=10)
    ax.set_yticks([0, 2, 4, 6]) # Ensure these specific ticks are present
    ax.set_yticklabels([severity_map.get(s, str(s)) for s in [0, 2, 4, 6]]) # Labels for y-axis
    plt.xticks(rotation=15, ha="right", fontsize=9) # Rotate x-axis labels slightly
    
    # Add text labels on top of bars
    for bar in bars.patches:
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height(), 
                severity_map.get(int(bar.get_height()), int(bar.get_height())),
                ha='center', va='bottom', color='black', fontsize=9)

    plt.tight_layout() # Adjust layout to prevent labels from overlapping

    # Save plot to a BytesIO buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100) # Lower dpi for smaller file size
    img_buffer.seek(0)
    
    # Encode image to Base64 string
    base64_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    plt.close(fig) # Close the figure to free memory
    
    return base64_img 