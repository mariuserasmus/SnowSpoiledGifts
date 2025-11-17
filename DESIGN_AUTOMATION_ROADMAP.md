# 🚀 Design Automation Roadmap
## Cookie Cutters & Cake Toppers - From Manual to Self-Service

**Goal:** Reduce design time from 30-60 minutes to under 5 minutes (or zero with self-service)

**Expected Business Impact:**
- 10x increase in daily capacity
- Faster quote turnaround (competitive advantage)
- Happier customers (instant previews)
- Higher profit margins (less labor time)
- Scale without hiring designers

---

## 📊 Current State vs Future State

| Metric | Current | Phase 1 | Phase 2 | Phase 3 (Self-Service) |
|--------|---------|---------|---------|------------------------|
| Design Time per Cookie Cutter | 30-60 min | 5-10 min | 2-5 min | 0 min (automated) |
| Design Time per Cake Topper | 45-90 min | 10-15 min | 5 min | 0 min (automated) |
| Daily Capacity | 3-5 items | 10-15 items | 20-30 items | Unlimited |
| Quote Response Time | 24-48 hours | 2-4 hours | 1 hour | Instant |
| Customer Satisfaction | Good | Great | Excellent | Outstanding |

---

## 🎯 Three-Phase Implementation Plan

### Phase 1: Quick Wins (Week 1-2)
**Time Investment:** 10-15 hours
**Cost:** $0 (all free tools)
**Time Savings:** 50-70% reduction

### Phase 2: Automation Scripts (Month 1-2)
**Time Investment:** 20-30 hours
**Cost:** $0-200 (optional paid tools)
**Time Savings:** 70-90% reduction

### Phase 3: Self-Service Portal (Month 2-4)
**Time Investment:** 40-80 hours (or hire developer)
**Cost:** $500-2000 (if outsourced)
**Time Savings:** 95%+ reduction

---

# PHASE 1: QUICK WINS (Start This Weekend!)

## 🍪 Cookie/Clay Cutter Fast Track

### Option A: Inkscape Auto-Trace Workflow
**Target: 5-10 minutes per cutter**

#### Tools Needed:
- [ ] Download & Install [Inkscape](https://inkscape.org/release/) (Free)
- [ ] Bookmark [svg2stl.com](https://svg2stl.com/) (Free online converter)
- [ ] Alternative: [selva3d.com](https://www.selva3d.com/en/online-tools/svg-to-stl) (More options)

#### Step-by-Step Workflow:

**1. Prepare Customer Image (2 minutes)**
- [ ] Open customer image in any image editor
- [ ] Increase contrast (black silhouette on white background works best)
- [ ] Crop to just the shape
- [ ] Save as PNG or JPG

**2. Auto-Trace in Inkscape (2 minutes)**
- [ ] Open Inkscape
- [ ] File → Import → Select customer image
- [ ] Select the image
- [ ] Path → Trace Bitmap
- [ ] Mode: "Brightness cutoff" (usually works best)
- [ ] Click "OK"
- [ ] Delete original bitmap image (keep only the traced path)
- [ ] Path → Simplify (reduces nodes, cleaner design)
- [ ] File → Save As → Plain SVG

**3. Convert SVG to STL (1 minute)**
- [ ] Go to svg2stl.com
- [ ] Upload your SVG file
- [ ] Set parameters:
  - Height: 10-15mm (standard cutter height)
  - Thickness: 1.2-1.5mm (wall thickness)
- [ ] Click "Convert"
- [ ] Download STL file

**4. Quick Cleanup in Fusion360 (2-5 minutes) - OPTIONAL**
- [ ] Import STL into Fusion360
- [ ] Mesh → Convert Mesh
- [ ] Add fillets to top edge (0.5mm radius) for strength
- [ ] Add chamfer to bottom edge (0.3mm) for clean cuts
- [ ] Export as STL

**Total Time: 5-10 minutes vs 30-60 minutes!**

#### Practice Exercise:
- [ ] Find a simple logo online (Nike swoosh, Apple logo, etc.)
- [ ] Run through the entire workflow
- [ ] Time yourself
- [ ] Repeat 3-5 times until comfortable

#### Tips & Tricks:
- High contrast images work best (black on white)
- Simple shapes trace better than complex ones
- If trace is messy, manually clean up SVG in Inkscape first
- Save your SVG files - customers often reorder!

---

### Option B: Cookie Caster Integration (Even Faster!)
**Target: 2-3 minutes per cutter**

- [ ] Visit [cookiecaster.com](https://www.cookiecaster.com/)
- [ ] Upload customer image
- [ ] Adjust size, depth, thickness
- [ ] Download STL
- [ ] Done!

**Note:** You could embed this tool on your website and charge markup!

---

## 🎂 Cake Topper Fast Track

### OpenSCAD Parametric Text Script
**Target: 30 seconds per topper**

#### Setup (One-Time, 1 hour):

**1. Install OpenSCAD**
- [ ] Download from [openscad.org](https://openscad.org/downloads.html)
- [ ] Install
- [ ] Open and familiarize with interface

**2. Create Your First Parametric Script**

Save this as `cake_topper_generator.scad`:

```openscad
// ===== CUSTOMIZABLE PARAMETERS =====
// Change these values for each order

// Text Settings
name = "Sarah";
font = "Arial:style=Bold";
text_size = 40;
text_thickness = 3;

// Base Settings
base_height = 5;
base_style = "oval"; // Options: "oval", "rectangle", "heart", "round"
base_padding = 10; // Extra space around text

// Advanced
add_stick_hole = true;
stick_diameter = 4;
stick_depth = 15;

// ===== DO NOT EDIT BELOW THIS LINE =====

module cake_topper() {
    difference() {
        union() {
            // Base shape
            if (base_style == "oval") {
                resize([text_size * len(name) * 0.6 + base_padding * 2,
                        text_size + base_padding * 2,
                        base_height])
                    cylinder(h=base_height, d=50, $fn=100);
            } else if (base_style == "rectangle") {
                cube([text_size * len(name) * 0.6 + base_padding * 2,
                      text_size + base_padding * 2,
                      base_height], center=true);
                translate([0, 0, base_height/2]) cube([text_size * len(name) * 0.6 + base_padding * 2,
                      text_size + base_padding * 2,
                      base_height], center=true);
            } else if (base_style == "heart") {
                // Simple heart approximation
                hull() {
                    translate([-text_size/4, text_size/4, 0])
                        cylinder(h=base_height, d=text_size/2, $fn=50);
                    translate([text_size/4, text_size/4, 0])
                        cylinder(h=base_height, d=text_size/2, $fn=50);
                    translate([0, -text_size/3, 0])
                        cylinder(h=base_height, d=text_size/3, $fn=50);
                }
            } else { // round
                cylinder(h=base_height, d=text_size * len(name) * 0.6 + base_padding * 2, $fn=100);
            }

            // Text
            translate([0, 0, base_height])
                linear_extrude(height=text_thickness)
                    text(name, size=text_size, font=font, halign="center", valign="center");
        }

        // Stick hole
        if (add_stick_hole) {
            translate([0, 0, -1])
                cylinder(h=stick_depth + 1, d=stick_diameter, $fn=30);
        }
    }
}

cake_topper();
```

**3. How to Use:**
- [ ] Open the .scad file in OpenSCAD
- [ ] Change the parameters at the top (name, font, style, etc.)
- [ ] Press F5 to preview
- [ ] Press F6 to render
- [ ] File → Export → Export as STL
- [ ] Done in 30 seconds!

**4. Create Variations:**
- [ ] Save different versions for common requests:
  - `topper_wedding.scad` (elegant fonts, heart base)
  - `topper_birthday.scad` (fun fonts, round base)
  - `topper_baby_shower.scad` (cute fonts, oval base)

**Practice:**
- [ ] Generate "Happy Birthday" topper
- [ ] Generate "Sarah & John" wedding topper
- [ ] Try different fonts and base styles
- [ ] Export 3-5 different variations

---

### Blender Text Workflow (More Complex Designs)
**Target: 10-15 minutes per topper**

**Setup:**
- [ ] Download [Blender](https://www.blender.org/download/) (Free)
- [ ] Install BlenderKit add-on (free 3D assets)
- [ ] Watch tutorial: "Blender Text to 3D" on YouTube (30 min)

**Workflow:**
- [ ] Add Text object (Shift+A → Text)
- [ ] Edit text (Tab key)
- [ ] Convert to Mesh (Object → Convert to → Mesh)
- [ ] Add Solidify modifier (for thickness)
- [ ] Add Remesh modifier (for clean geometry)
- [ ] Add base shape (cube, cylinder, imported SVG)
- [ ] Boolean union text + base
- [ ] Export as STL

**Use Cases:**
- Complex multi-line toppers
- Toppers with decorative elements
- Toppers requiring manual artistic touch

---

## ✅ Phase 1 Success Checklist

By end of Week 2, you should be able to:

**Cookie Cutters:**
- [ ] Receive customer image
- [ ] Generate print-ready STL in under 10 minutes
- [ ] Consistent quality every time
- [ ] 50%+ time savings

**Cake Toppers:**
- [ ] Receive customer text/name
- [ ] Generate STL in under 5 minutes using OpenSCAD
- [ ] Multiple base style options
- [ ] 70%+ time savings

**Business Impact:**
- [ ] Process 2-3x more orders per day
- [ ] Send quotes same-day instead of next-day
- [ ] More time for marketing and sales

---

# PHASE 2: AUTOMATION SCRIPTS (Month 1-2)

## 🎯 Goal: Eliminate Repetitive Steps

### Cookie Cutter: Python Automation Script

**What it does:**
- Customer uploads image through your website
- Script auto-traces image
- Generates STL with standard specifications
- Saves to folder named by order number
- Sends confirmation email with preview

**Tools Needed:**
- [ ] Python (already have via Flask)
- [ ] Install libraries:
  ```bash
  pip install potrace
  pip install pillow
  pip install numpy-stl
  pip install svgwrite
  ```

**Implementation Steps:**

**1. Create Image Processing Script**

Save as `scripts/generate_cookie_cutter.py`:

```python
#!/usr/bin/env python3
"""
Cookie Cutter STL Generator
Converts uploaded images to print-ready cookie cutter STLs
"""

import os
import subprocess
from PIL import Image, ImageOps, ImageEnhance
import numpy as np

def process_image_to_svg(image_path, output_svg_path):
    """
    Process image and convert to SVG using potrace
    """
    # Load and preprocess image
    img = Image.open(image_path)

    # Convert to grayscale
    img = img.convert('L')

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # Convert to black and white
    img = img.point(lambda x: 0 if x < 128 else 255, '1')

    # Save as temporary BMP for potrace
    temp_bmp = image_path.replace('.png', '_temp.bmp').replace('.jpg', '_temp.bmp')
    img.save(temp_bmp)

    # Run potrace to convert to SVG
    subprocess.run([
        'potrace',
        temp_bmp,
        '-s',  # SVG output
        '-o', output_svg_path,
        '-t', '10',  # Suppress speckles of up to 10 pixels
        '-O', '0.2'  # Curve optimization
    ])

    # Clean up temp file
    os.remove(temp_bmp)

    return output_svg_path

def svg_to_stl(svg_path, stl_path, height=12, thickness=1.2):
    """
    Convert SVG to STL using OpenSCAD
    """
    scad_template = f"""
    linear_extrude(height = {height})
        import("{svg_path}");
    """

    # Save temporary SCAD file
    temp_scad = svg_path.replace('.svg', '.scad')
    with open(temp_scad, 'w') as f:
        f.write(scad_template)

    # Run OpenSCAD to generate STL
    subprocess.run([
        'openscad',
        '-o', stl_path,
        temp_scad
    ])

    # Clean up
    os.remove(temp_scad)

    return stl_path

def generate_cookie_cutter(image_path, output_dir, order_id):
    """
    Full pipeline: Image -> SVG -> STL
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate filenames
    svg_path = os.path.join(output_dir, f'{order_id}_cutter.svg')
    stl_path = os.path.join(output_dir, f'{order_id}_cutter.stl')

    # Process
    print(f"Processing {image_path}...")
    process_image_to_svg(image_path, svg_path)
    print(f"SVG created: {svg_path}")

    svg_to_stl(svg_path, stl_path)
    print(f"STL created: {stl_path}")

    return stl_path

if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 4:
        print("Usage: python generate_cookie_cutter.py <image_path> <output_dir> <order_id>")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2]
    order_id = sys.argv[3]

    stl_file = generate_cookie_cutter(image_path, output_dir, order_id)
    print(f"✓ Cookie cutter STL ready: {stl_file}")
```

**2. Integrate with Flask App**

Add to `app.py`:

```python
@app.route('/admin/generate-cutter/<int:quote_id>', methods=['POST'])
@admin_required
def generate_cutter_from_quote(quote_id):
    """Auto-generate cookie cutter STL from quote"""
    from scripts.generate_cookie_cutter import generate_cookie_cutter

    # Get quote details
    quote = db.get_quote_request(quote_id)

    if not quote or not quote['reference_images']:
        return jsonify({'success': False, 'message': 'No image found'}), 400

    # Get first image
    image_filename = quote['reference_images'].split(',')[0].strip()
    image_path = os.path.join('static', 'uploads', 'cutter_references', image_filename)

    if not os.path.exists(image_path):
        return jsonify({'success': False, 'message': 'Image file not found'}), 404

    # Generate STL
    output_dir = os.path.join('static', 'generated_stls', 'cutters')
    order_id = f"QUOTE-{quote_id}"

    try:
        stl_path = generate_cookie_cutter(image_path, output_dir, order_id)

        return jsonify({
            'success': True,
            'message': 'STL generated successfully!',
            'stl_path': stl_path.replace('\\', '/'),
            'download_url': f"/static/generated_stls/cutters/{order_id}_cutter.stl"
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**3. Add "Auto-Generate STL" Button to Admin Panel**

In `templates/admin-quotes.html`, add button in quote detail modal:

```html
{% if quote.request_type in ['cookie_clay_cutter'] and quote.reference_images %}
<button class="btn btn-primary" onclick="generateCutterSTL({{ quote.id }})">
    <i class="fas fa-magic"></i> Auto-Generate Cutter STL
</button>

<script>
function generateCutterSTL(quoteId) {
    if (!confirm('Generate cookie cutter STL from uploaded image?')) return;

    fetch(`/admin/generate-cutter/${quoteId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('STL generated! Download: ' + data.download_url);
            // Auto-download
            window.open(data.download_url, '_blank');
        } else {
            alert('Error: ' + data.message);
        }
    });
}
</script>
{% endif %}
```

**Installation:**
- [ ] Install potrace: `sudo apt install potrace` (Linux) or `brew install potrace` (Mac)
- [ ] Install OpenSCAD command-line
- [ ] Test script with sample image
- [ ] Integrate into admin panel

---

### Cake Topper: Web Form to STL Pipeline

**What it does:**
- Customer fills out form (name, font, base style)
- Script generates STL using OpenSCAD
- Customer sees 3D preview
- Downloads STL or adds to cart

**Implementation:**

**1. Create OpenSCAD Generator Script**

Save as `scripts/generate_cake_topper.py`:

```python
#!/usr/bin/env python3
"""
Cake Topper STL Generator
Generates parametric cake toppers from text input
"""

import os
import subprocess

def generate_topper_scad(name, font="Arial:style=Bold", text_size=40,
                         base_style="oval", output_path=None):
    """
    Generate OpenSCAD file for cake topper
    """
    scad_content = f"""
// Auto-generated cake topper
name = "{name}";
font = "{font}";
text_size = {text_size};
text_thickness = 3;
base_height = 5;
base_style = "{base_style}";
base_padding = 10;
add_stick_hole = true;
stick_diameter = 4;
stick_depth = 15;

module cake_topper() {{
    difference() {{
        union() {{
            // Base shape
            if (base_style == "oval") {{
                resize([text_size * len(name) * 0.6 + base_padding * 2,
                        text_size + base_padding * 2,
                        base_height])
                    cylinder(h=base_height, d=50, $fn=100);
            }} else if (base_style == "rectangle") {{
                translate([0, 0, base_height/2])
                    cube([text_size * len(name) * 0.6 + base_padding * 2,
                          text_size + base_padding * 2,
                          base_height], center=true);
            }} else if (base_style == "round") {{
                cylinder(h=base_height, d=text_size * len(name) * 0.6 + base_padding * 2, $fn=100);
            }}

            // Text
            translate([0, 0, base_height])
                linear_extrude(height=text_thickness)
                    text(name, size=text_size, font=font, halign="center", valign="center");
        }}

        // Stick hole
        if (add_stick_hole) {{
            translate([0, 0, -1])
                cylinder(h=stick_depth + 1, d=stick_diameter, $fn=30);
        }}
    }}
}}

cake_topper();
"""

    if not output_path:
        output_path = f"temp_topper_{name.replace(' ', '_')}.scad"

    with open(output_path, 'w') as f:
        f.write(scad_content)

    return output_path

def scad_to_stl(scad_path, stl_path):
    """
    Convert SCAD to STL using OpenSCAD CLI
    """
    subprocess.run([
        'openscad',
        '-o', stl_path,
        scad_path
    ], check=True)

    return stl_path

def generate_cake_topper(name, font="Arial:style=Bold", base_style="oval",
                         output_dir="static/generated_stls/toppers", order_id=None):
    """
    Full pipeline: Parameters -> SCAD -> STL
    """
    os.makedirs(output_dir, exist_ok=True)

    if not order_id:
        order_id = name.replace(' ', '_')

    scad_path = os.path.join(output_dir, f'{order_id}.scad')
    stl_path = os.path.join(output_dir, f'{order_id}.stl')

    # Generate SCAD
    generate_topper_scad(name, font, 40, base_style, scad_path)

    # Convert to STL
    scad_to_stl(scad_path, stl_path)

    # Clean up SCAD file (optional)
    # os.remove(scad_path)

    return stl_path

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_cake_topper.py <name> [font] [base_style]")
        sys.exit(1)

    name = sys.argv[1]
    font = sys.argv[2] if len(sys.argv) > 2 else "Arial:style=Bold"
    base_style = sys.argv[3] if len(sys.argv) > 3 else "oval"

    stl_file = generate_cake_topper(name, font, base_style)
    print(f"✓ Cake topper STL ready: {stl_file}")
```

**2. Flask Route for Topper Generation**

```python
@app.route('/admin/generate-topper/<int:quote_id>', methods=['POST'])
@admin_required
def generate_topper_from_quote(quote_id):
    """Auto-generate cake topper STL from quote"""
    from scripts.generate_cake_topper import generate_cake_topper

    # Get form data
    name = request.form.get('topper_name')
    font = request.form.get('topper_font', 'Arial:style=Bold')
    base_style = request.form.get('base_style', 'oval')

    if not name:
        return jsonify({'success': False, 'message': 'Name required'}), 400

    try:
        output_dir = 'static/generated_stls/toppers'
        order_id = f"QUOTE-{quote_id}_{name.replace(' ', '_')}"

        stl_path = generate_cake_topper(name, font, base_style, output_dir, order_id)

        return jsonify({
            'success': True,
            'message': 'Cake topper STL generated!',
            'stl_path': stl_path.replace('\\', '/'),
            'download_url': f"/static/generated_stls/toppers/{order_id}.stl"
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

---

## ✅ Phase 2 Success Checklist

By end of Month 2, you should have:

**Automation:**
- [ ] Cookie cutter auto-generation from admin panel
- [ ] Cake topper generation with web form
- [ ] One-click STL generation
- [ ] Automated file naming and organization

**Time Savings:**
- [ ] Cookie cutters: 2-5 minutes (down from 30-60 min)
- [ ] Cake toppers: 1-2 minutes (down from 45-90 min)
- [ ] 70-90% time reduction overall

**Capacity:**
- [ ] Handle 15-20 orders per day
- [ ] Same-day quote responses
- [ ] More time for customer service and marketing

---

# PHASE 3: SELF-SERVICE PORTAL (Month 2-4)

## 🎯 Ultimate Goal: Zero Design Time

**Customer Experience:**
1. Visit your website
2. Use interactive customizer
3. See 3D preview in real-time
4. Click "Add to Cart" - R150
5. You receive order notification
6. You just print and ship!

**Your Time:** 0 minutes of design work!

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         Customer-Facing Website                 │
│                                                 │
│  ┌──────────────┐      ┌──────────────┐       │
│  │  Cookie      │      │  Cake        │       │
│  │  Cutter      │      │  Topper      │       │
│  │  Customizer  │      │  Customizer  │       │
│  └──────┬───────┘      └──────┬───────┘       │
│         │                     │                │
│         └──────────┬──────────┘                │
│                    │                           │
│              3D Preview                        │
│            (Three.js viewer)                   │
│                    │                           │
│         ┌──────────▼──────────┐                │
│         │   Add to Cart       │                │
│         └──────────┬──────────┘                │
└────────────────────┼────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   Flask Backend       │
         │                       │
         │  - Validate params    │
         │  - Generate STL       │
         │  - Store in DB        │
         │  - Send notification  │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  Background Worker    │
         │  (STL Generation)     │
         │                       │
         │  - Run OpenSCAD       │
         │  - Run potrace        │
         │  - Save STL file      │
         └───────────────────────┘
```

---

## Component 1: Cookie Cutter Customizer

### Frontend (HTML/JavaScript)

Create `templates/customize_cookie_cutter.html`:

```html
{% extends "base.html" %}

{% block title %}Custom Cookie Cutter Designer{% endblock %}

{% block extra_css %}
<style>
    .customizer-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        padding: 30px;
    }

    .controls-panel {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .preview-panel {
        background: #f5f5f5;
        padding: 30px;
        border-radius: 10px;
        min-height: 500px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    #stl-preview {
        width: 100%;
        height: 400px;
        background: white;
        border-radius: 8px;
    }

    .upload-zone {
        border: 3px dashed #ccc;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }

    .upload-zone:hover {
        border-color: #007bff;
        background: #f8f9ff;
    }

    .upload-zone.dragover {
        border-color: #28a745;
        background: #f0fff4;
    }

    .preview-image {
        max-width: 100%;
        max-height: 200px;
        margin: 20px 0;
    }

    .param-group {
        margin-bottom: 25px;
    }

    .param-group label {
        display: block;
        font-weight: 600;
        margin-bottom: 8px;
        color: #333;
    }

    .param-group input[type="range"] {
        width: 100%;
    }

    .param-value {
        float: right;
        color: #007bff;
        font-weight: 600;
    }

    .price-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }

    .price-display h3 {
        margin: 0;
        font-size: 2rem;
    }

    .btn-generate {
        width: 100%;
        padding: 15px;
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12 text-center my-4">
            <h1><i class="fas fa-cookie-bite"></i> Custom Cookie Cutter Designer</h1>
            <p class="text-muted">Upload your design and customize your perfect cookie cutter</p>
        </div>
    </div>

    <div class="customizer-container">
        <!-- Controls Panel -->
        <div class="controls-panel">
            <h4><i class="fas fa-sliders-h"></i> Design Options</h4>
            <hr>

            <!-- Upload Image -->
            <div class="param-group">
                <label>Upload Your Design</label>
                <div class="upload-zone" id="uploadZone">
                    <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                    <p>Drag & drop your image here<br>or click to browse</p>
                    <input type="file" id="imageUpload" accept="image/*" style="display: none;">
                </div>
                <img id="uploadedImage" class="preview-image" style="display: none;">
            </div>

            <!-- Size -->
            <div class="param-group">
                <label>
                    Size (Width)
                    <span class="param-value" id="sizeValue">80mm</span>
                </label>
                <input type="range" id="size" min="40" max="150" value="80" step="5">
                <small class="text-muted">Standard cookie size: 70-90mm</small>
            </div>

            <!-- Height -->
            <div class="param-group">
                <label>
                    Cutter Height
                    <span class="param-value" id="heightValue">12mm</span>
                </label>
                <input type="range" id="height" min="8" max="20" value="12" step="1">
                <small class="text-muted">Recommended: 10-15mm</small>
            </div>

            <!-- Wall Thickness -->
            <div class="param-group">
                <label>
                    Wall Thickness
                    <span class="param-value" id="thicknessValue">1.2mm</span>
                </label>
                <input type="range" id="thickness" min="0.8" max="2.0" value="1.2" step="0.1">
                <small class="text-muted">Standard: 1.0-1.5mm</small>
            </div>

            <!-- Handle Style -->
            <div class="param-group">
                <label>Handle Style</label>
                <select class="form-select" id="handleStyle">
                    <option value="none">No Handle</option>
                    <option value="top" selected>Top Handle</option>
                    <option value="side">Side Handle</option>
                </select>
            </div>

            <!-- Price Display -->
            <div class="price-display">
                <p class="mb-1">Total Price</p>
                <h3 id="priceDisplay">R150</h3>
                <small>Includes design + printing + shipping</small>
            </div>

            <!-- Action Buttons -->
            <button class="btn btn-primary btn-generate mb-2" onclick="generatePreview()" disabled id="btnPreview">
                <i class="fas fa-eye"></i> Generate 3D Preview
            </button>
            <button class="btn btn-success btn-generate" onclick="addToCart()" disabled id="btnAddCart">
                <i class="fas fa-cart-plus"></i> Add to Cart - R<span id="cartPrice">150</span>
            </button>
        </div>

        <!-- Preview Panel -->
        <div class="preview-panel">
            <h4><i class="fas fa-cube"></i> 3D Preview</h4>
            <div id="stl-preview">
                <div style="padding: 100px; text-align: center; color: #999;">
                    <i class="fas fa-image fa-5x mb-3"></i>
                    <p>Upload an image to see preview</p>
                </div>
            </div>
            <div class="mt-3">
                <small class="text-muted">
                    <i class="fas fa-info-circle"></i> Drag to rotate • Scroll to zoom
                </small>
            </div>
        </div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
let uploadedFile = null;
let scene, camera, renderer, controls;
let currentSTL = null;

// Initialize 3D viewer
function init3DViewer() {
    const container = document.getElementById('stl-preview');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    // Camera
    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 1, 1000);
    camera.position.set(0, 0, 150);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;

    // Lights
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    // Grid
    const gridHelper = new THREE.GridHelper(200, 20);
    scene.add(gridHelper);

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}

// Upload handling
const uploadZone = document.getElementById('uploadZone');
const imageUpload = document.getElementById('imageUpload');
const uploadedImage = document.getElementById('uploadedImage');

uploadZone.addEventListener('click', () => imageUpload.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    handleFile(e.dataTransfer.files[0]);
});

imageUpload.addEventListener('change', (e) => {
    handleFile(e.target.files[0]);
});

function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
    }

    uploadedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedImage.src = e.target.result;
        uploadedImage.style.display = 'block';
        uploadZone.style.display = 'none';
        document.getElementById('btnPreview').disabled = false;
    };
    reader.readAsDataURL(file);
}

// Parameter updates
document.getElementById('size').addEventListener('input', (e) => {
    document.getElementById('sizeValue').textContent = e.target.value + 'mm';
    updatePrice();
});

document.getElementById('height').addEventListener('input', (e) => {
    document.getElementById('heightValue').textContent = e.target.value + 'mm';
});

document.getElementById('thickness').addEventListener('input', (e) => {
    document.getElementById('thicknessValue').textContent = e.target.value + 'mm';
});

function updatePrice() {
    const size = parseInt(document.getElementById('size').value);
    let price = 150; // Base price

    // Price increases with size
    if (size > 100) price = 180;
    if (size > 120) price = 220;

    document.getElementById('priceDisplay').textContent = 'R' + price;
    document.getElementById('cartPrice').textContent = price;
}

// Generate preview
function generatePreview() {
    if (!uploadedFile) {
        alert('Please upload an image first');
        return;
    }

    const btn = document.getElementById('btnPreview');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

    // Create FormData
    const formData = new FormData();
    formData.append('image', uploadedFile);
    formData.append('size', document.getElementById('size').value);
    formData.append('height', document.getElementById('height').value);
    formData.append('thickness', document.getElementById('thickness').value);
    formData.append('handle', document.getElementById('handleStyle').value);

    // Send to backend
    fetch('/api/generate-cutter-preview', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadSTLPreview(data.stl_url);
            document.getElementById('btnAddCart').disabled = false;
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error generating preview: ' + error);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-eye"></i> Generate 3D Preview';
    });
}

function loadSTLPreview(stlUrl) {
    // Remove old STL
    if (currentSTL) {
        scene.remove(currentSTL);
    }

    // Load new STL
    const loader = new THREE.STLLoader();
    loader.load(stlUrl, (geometry) => {
        const material = new THREE.MeshPhongMaterial({
            color: 0x00a8ff,
            specular: 0x111111,
            shininess: 200
        });

        const mesh = new THREE.Mesh(geometry, material);

        // Center and scale
        geometry.computeBoundingBox();
        const center = geometry.boundingBox.getCenter(new THREE.Vector3());
        mesh.position.sub(center);

        scene.add(mesh);
        currentSTL = mesh;

        // Adjust camera
        const size = geometry.boundingBox.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        camera.position.set(maxDim * 1.5, maxDim * 1.5, maxDim * 1.5);
        camera.lookAt(0, 0, 0);
    });
}

function addToCart() {
    const price = document.getElementById('cartPrice').textContent;

    if (confirm(`Add custom cookie cutter to cart for R${price}?`)) {
        // Add to cart via API
        fetch('/cart/add-custom-cutter', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: 'Custom Cookie Cutter - ' + uploadedFile.name,
                price: price,
                size: document.getElementById('size').value,
                height: document.getElementById('height').value,
                thickness: document.getElementById('thickness').value,
                handle: document.getElementById('handleStyle').value,
                image_filename: uploadedFile.name
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Added to cart!');
                window.location.href = '/cart';
            } else {
                alert('Error: ' + data.message);
            }
        });
    }
}

// Initialize on load
window.addEventListener('load', () => {
    init3DViewer();
});
</script>
{% endblock %}
```

### Backend API Routes

Add to `app.py`:

```python
@app.route('/api/generate-cutter-preview', methods=['POST'])
def generate_cutter_preview():
    """Generate cookie cutter STL preview from uploaded image"""
    from scripts.generate_cookie_cutter import generate_cookie_cutter
    import uuid

    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image uploaded'}), 400

    image = request.files['image']
    size = request.form.get('size', 80)
    height = request.form.get('height', 12)
    thickness = request.form.get('thickness', 1.2)

    # Generate unique ID for this preview
    preview_id = str(uuid.uuid4())[:8]

    # Save uploaded image
    temp_dir = os.path.join('static', 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)

    image_path = os.path.join(temp_dir, f'{preview_id}_{image.filename}')
    image.save(image_path)

    # Generate STL
    try:
        output_dir = os.path.join('static', 'temp_stls')
        stl_path = generate_cookie_cutter(image_path, output_dir, preview_id)

        # Return URL for 3D viewer
        stl_url = f"/static/temp_stls/{preview_id}_cutter.stl"

        return jsonify({
            'success': True,
            'stl_url': stl_url,
            'preview_id': preview_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/cart/add-custom-cutter', methods=['POST'])
@login_required
def add_custom_cutter_to_cart():
    """Add customized cookie cutter to cart"""
    data = request.json

    # Create custom item in database
    # (Use your existing add_to_cart logic but with custom item)

    return jsonify({'success': True, 'message': 'Added to cart!'})
```

---

## Component 2: Cake Topper Customizer

**Similar structure to cookie cutter, but simpler:**

- Text input field
- Font dropdown (5-10 popular fonts)
- Base style selector (oval, rectangle, heart, round)
- Size slider
- Real-time 3D preview using Three.js
- "Add to Cart" button

Implementation details in next section...

---

## 🛠️ Technical Stack

### Frontend:
- **Three.js** - 3D visualization
- **Bootstrap 5** - UI framework
- **JavaScript** - Interactivity

### Backend:
- **Flask** - Web framework (already have)
- **OpenSCAD** - STL generation
- **Potrace** - Image tracing
- **Pillow** - Image processing
- **Celery** (optional) - Background job processing

### Infrastructure:
- **Static file storage** for generated STLs
- **Redis** (optional) - Job queue for Celery
- **Nginx** - Serve static STL files efficiently

---

## Implementation Approach

### Option A: Build In-House
**Pros:**
- Full control
- No ongoing costs
- Custom features

**Cons:**
- 40-80 hours development time
- Requires technical skills
- Maintenance burden

**Estimated Time:**
- Cookie cutter customizer: 20-30 hours
- Cake topper customizer: 15-20 hours
- Testing & refinement: 10-15 hours
- **Total: 45-65 hours**

### Option B: Hire Developer
**Pros:**
- Professional quality
- Faster delivery
- Less stress

**Cons:**
- Upfront cost ($500-2000)
- Communication overhead
- Still need to maintain

**Platforms:**
- Fiverr (South African developers)
- Upwork
- Local freelancers

**Budget:**
- Basic customizer: R5,000 - R10,000
- Advanced with 3D preview: R15,000 - R30,000

### Option C: Use Existing Tools
**Pros:**
- Immediate
- No development
- Proven solutions

**Cons:**
- Monthly fees
- Less customization
- Dependency on third party

**Options:**
- Embed cookiecaster.com widget ($50-100/month)
- Use Thingiverse Customizer
- Partner with existing platforms

---

## 📈 Business Model Integration

### Pricing Strategy

**Cookie Cutters:**
- Standard size (60-90mm): R150
- Large (90-120mm): R180
- XL (120mm+): R220
- Bulk orders (10+): 15% discount

**Cake Toppers:**
- Single name/word: R180
- Two lines (name + date): R220
- Custom design consultation: R350+

### Upsells:
- Rush order (+R50, 24hr turnaround)
- Gift box packaging (+R30)
- Multiple quantities (discount pricing)

### Marketing Copy:

**Cookie Cutter Page:**
> "Design Your Perfect Cookie Cutter in 60 Seconds"
>
> Upload your logo, design, or idea and watch it transform into a custom cookie cutter. Food-safe PLA, ready to use, delivered in 3-5 days. Starting from R150.

**Cake Topper Page:**
> "Personalized Cake Toppers for Your Special Day"
>
> Add a custom touch to your celebration. Choose your text, font, and style. Preview in 3D before ordering. Starting from R180.

---

## ✅ Phase 3 Success Checklist

By end of Month 4, you should have:

**Customer Self-Service:**
- [ ] Cookie cutter customizer live on website
- [ ] Cake topper customizer live on website
- [ ] Real-time 3D previews working
- [ ] Automated ordering and payment
- [ ] Email confirmations to customers
- [ ] Print queue for you (just print & ship!)

**Business Metrics:**
- [ ] 50+ customizations per month
- [ ] 95%+ time savings on design
- [ ] Same-day order processing
- [ ] Higher customer satisfaction
- [ ] More revenue (higher capacity)

**Marketing:**
- [ ] "Design Your Own" featured on homepage
- [ ] Social media posts showcasing customizer
- [ ] Customer testimonials and examples
- [ ] SEO optimized for "custom cookie cutter" searches

---

# 📚 Resources & Learning

## Free Tutorials

**OpenSCAD:**
- [Official Tutorial](https://openscad.org/documentation.html)
- YouTube: "OpenSCAD for Beginners"
- Practice projects: Parametric designs

**Inkscape:**
- [Inkscape Tutorials](https://inkscape.org/learn/tutorials/)
- YouTube: "Inkscape Trace Bitmap Tutorial"

**Three.js:**
- [Three.js Fundamentals](https://threejs.org/manual/)
- YouTube: "Three.js STL Viewer Tutorial"

**Python Image Processing:**
- Pillow documentation
- Potrace integration guides

## Community Support

- **Thingiverse Forums** - 3D printing community
- **r/3Dprinting** subreddit
- **OpenSCAD Forum** - Parametric design help
- **Stack Overflow** - Coding questions

## Tools to Install

**Essential:**
- [ ] OpenSCAD
- [ ] Inkscape
- [ ] Python libraries (Pillow, potrace, etc.)

**Nice to Have:**
- [ ] Blender
- [ ] MeshLab (STL cleanup)
- [ ] Simplify3D/Cura (print preview)

---

# 💰 Cost Breakdown

## Phase 1: Quick Wins
- **Software:** $0 (all free)
- **Time:** 10-15 hours (your time)
- **Total:** FREE

## Phase 2: Automation
- **Software:** $0
- **Hosting upgrades:** $0-50/month (if needed for processing)
- **Time:** 20-30 hours
- **Total:** $0-50

## Phase 3: Self-Service Portal

### Option 1: DIY
- **Development:** $0 (your time: 40-80 hours)
- **Hosting:** $10-30/month increase
- **Total:** $10-30/month

### Option 2: Hire Developer
- **Development:** R15,000-30,000 one-time
- **Hosting:** $10-30/month
- **Total:** R15,000-30,000 + $30/month

### Option 3: Use Existing Platform
- **Integration:** R5,000-10,000
- **Monthly fees:** $50-200/month
- **Total:** R5,000 + $100/month avg

---

# 📊 ROI Calculator

## Current State (Manual Design):
- Design time per item: 45 min average
- Hourly rate (your time): R300
- **Cost per design:** R225
- Daily capacity: 5 items
- Monthly capacity: ~100 items

## Phase 1 (70% time savings):
- Design time: 13 min average
- **Cost per design:** R65
- Daily capacity: 15 items
- Monthly capacity: ~300 items
- **Savings:** R160 per item = R16,000/month at 100 items

## Phase 3 (95% time savings):
- Design time: 2 min average
- **Cost per design:** R10
- Daily capacity: 50+ items
- Monthly capacity: unlimited
- **Savings:** R215 per item = R21,500/month at 100 items

### Break-Even:
- DIY Phase 3: Immediate (no cost)
- Hire developer (R20,000): **1 month** of 100 items
- Platform fee ($100/mo): Pays for itself with **1 extra order/month**

---

# 🎯 Action Plan Summary

## Week 1-2: Learn & Practice
- [ ] Install all software (OpenSCAD, Inkscape)
- [ ] Practice Inkscape → SVG → STL workflow
- [ ] Create first OpenSCAD parametric script
- [ ] Generate 5-10 test STLs
- [ ] Measure time savings

## Month 1: Implement Automation
- [ ] Create Python scripts for automation
- [ ] Add "Auto-Generate" buttons to admin panel
- [ ] Test with real customer orders
- [ ] Collect feedback
- [ ] Refine workflow

## Month 2-3: Plan Self-Service
- [ ] Decide: DIY, hire, or use platform
- [ ] If DIY: Start frontend development
- [ ] If hire: Post job, interview developers
- [ ] Design UI/UX mockups
- [ ] Set up infrastructure (hosting, storage)

## Month 3-4: Launch Self-Service
- [ ] Build/receive customizer
- [ ] Test thoroughly with beta users
- [ ] Launch publicly
- [ ] Market heavily (social media, ads)
- [ ] Monitor and optimize

## Ongoing:
- [ ] Collect customer feedback
- [ ] Add new features (more fonts, designs)
- [ ] Expand to new product types
- [ ] Build template library
- [ ] Scale marketing

---

# 🚀 Next Steps - Choose Your Path

## Path A: Start Immediately (Recommended)
**This weekend:**
1. Install Inkscape and OpenSCAD
2. Practice image → STL workflow
3. Generate your first automated STL
4. Time yourself - see the savings!

**I can help you:**
- Write the OpenSCAD cake topper script
- Create step-by-step Inkscape guide
- Review your first test outputs

## Path B: Plan First
**This week:**
1. Review this document
2. Decide on timeline and budget
3. Choose DIY vs hire approach
4. Set milestones and deadlines

**I can help you:**
- Refine the plan
- Provide code examples
- Answer technical questions

## Path C: Outsource Everything
**Contact developers:**
1. Post job on Fiverr/Upwork
2. Interview candidates
3. Show them this document as spec
4. Get quotes and timelines

**I can help you:**
- Write technical requirements
- Review proposals
- Provide developer oversight

---

# 📞 Support & Questions

As you work through this roadmap, I'm here to help:

- **OpenSCAD scripting** - I can write scripts for you
- **Python automation** - Code reviews and debugging
- **Flask integration** - Backend development help
- **Three.js 3D viewer** - Frontend implementation
- **Architecture questions** - System design advice
- **Marketing copy** - Sales page content

**Just ask and I'll jump in!**

---

# 🎉 Final Thoughts

This automation journey will:
- **10x your capacity** (from 5 to 50+ items/day)
- **Cut costs** by 95% (R225 → R10 per design)
- **Delight customers** (instant previews, faster turnaround)
- **Scale your business** (no hiring needed)
- **Increase profits** (more orders, less time)

**The cookie cutter and cake topper market is PERFECT for automation.**

You're not competing with hobbyists - you're offering a professional service that saves customers time and delivers quality. The self-service portal makes you the "easy button" for bakers and event planners.

**This is your competitive advantage. Let's build it!**

---

**Ready to start? Pick a Phase 1 task and let me know how I can help!** 🚀

---

*Last Updated: 2025-11-15*
*Next Review: After Phase 1 completion*
